#!/usr/bin/env python
#
# This observer tracks text conversation and reports events to the Zeitgeist
# engine. Eventually, it will report file transfers and media streams
#
# ZConnections and ZChannels are tracked by the ZObserver, their invalidation
# is signalled by GObject signals. ZObserver.ObserveChannels uses asynchronous
# return functions to only return from the D-Bus method once all of the channels
# are prepared, this gives the Observer time to investigate the pending message
# queue before any Handlers can acknowledge it.
#
# Authors: Danielle Madeley <danielle.madeley@collabora.co.uk>
#          Morten Mjelva <morten.mjelva@gmail.com>
#
import dbus, dbus.glib
import gobject

import sys

from time import time

import logging
logging.basicConfig(level=logging.DEBUG)

import telepathy
from telepathy.constants import CONNECTION_STATUS_DISCONNECTED, \
                                HANDLE_TYPE_CONTACT

from telepathy.interfaces import CHANNEL, \
                                 CHANNEL_TYPE_FILE_TRANSFER, \
                                 CHANNEL_TYPE_STREAMED_MEDIA, \
                                 CHANNEL_TYPE_TEXT, \
                                 CLIENT, \
                                 CLIENT_OBSERVER, \
                                 CONNECTION, \
                                 CONNECTION_INTERFACE_ALIASING, \
                                 CONNECTION_INTERFACE_CONTACTS

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

def error(*args):
    logging.error("error %s" % args)

# Create a connection to the Zeitgeist engine
try:
    zclient = ZeitgeistClient()
except RuntimeError, e:
    logging.error("Unable to connect to Zeitgeist. Won't send events. Reason: \
            %s" % e)
    zclient = None

class ZConnection(gobject.GObject, telepathy.client.Connection):
    """
    Extends telepathy.client.Connection, storing information about proxy obj

    Object extends tp.Connection object, letting us store information about the
    connection proxy locally.
    Arguments:
        path: Unique path to this connection
        ready_handler: Callback function run once we're done setting up object
    """
    __gsignals__ = {
            'disconnected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            }

    def __init__(self, path, ready_handler):
        service_name = path.replace('/', '.')[1:]

        # Ready callback
        self.ready_handler = ready_handler
        self.signals = []

        gobject.GObject.__init__(self)
        telepathy.client.Connection.__init__(self, service_name, path,
                ready_handler = self._connection_ready)

    def __repr__(self):
        return "ZConnection(%s)" % self.object_path

    def _status_changed(self, status, reason):
        if status == CONNECTION_STATUS_DISCONNECTED:
            for signal in self.signals:
                signal.remove()

            self.emit('disconnected')

    def _connection_ready(self, conn):
        def interfaces(interfaces):
            self.contact_attr_interfaces = interfaces

        # Connection ready
        self.ready_handler(conn)

        # Get contact attribute interfaces
        self[dbus.PROPERTIES_IFACE].Get(CONNECTION_INTERFACE_CONTACTS,
                'ContactAttributeInterfaces',
                reply_handler=interfaces,
                error_handler=error)
        
        self.signals.append(self[CONNECTION].connect_to_signal(
            'StatusChanged', self._status_changed))

    # This is necessary so our signal isn't sent over D-Bus
    def do_disconnected(self):
        pass
gobject.type_register(ZConnection)

class ZChannel(gobject.GObject, telepathy.client.Channel):
    """
    Extends telepathy.client.Channel

    This class allows us to store information about a telepathy.client.Channel
    object locally.
    Arguments:
    account_path: Path to the account used. Passed to ObserveChannels.
    connection: The connection used for the channel
    properties: Properties of the channel we're proxying, from ObserveChannels
    ready_handler: Callback function run once we're done setting up object
    """
    __gsignals__ = { 
            'closed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            }

    def __init__(self, account_path, connection, path, properties, ready_handler):
        self.account_path = account_path
        self.conn = connection
        self.properties = properties
        self.ready_handler = ready_handler

        self.signals = []

        gobject.GObject.__init__(self)
        telepathy.client.Channel.__init__(self, connection.service_name, path,
                ready_handler=self._channel_ready)

    def __repr__(self):
        return "ZChannel(%s)" % self.object_path

    def _send_to_zeitgeist(self, subjects, event_details):
        event_details['subjects'] = subjects
        zevent = Event.new_for_values(**event_details)
        zclient.insert_event(zevent)

    def _channel_closed_cb(self):
        for signal in self.signals:
            signal.remove()

        self.emit('closed')

    def _default_operations_finished(self):
        self._release_channel()

    def _get_contact_attributes_cb(self, attributes_map):
        handle = self.properties[CHANNEL + '.TargetHandle']
        try:
            attributes = attributes_map[handle]
            self._target_alias = attributes[CONNECTION_INTERFACE_ALIASING +
                    '/alias']
        except KeyError:
            self._target_alias = self._target_id
        
        self._connect_to_signals()
        self._default_operations_finished()

    def _get_requested_cb(self, req):
        handle = self.properties[CHANNEL + '.TargetHandle']
        self._channel_requested = req

        # Get contact name
        self.conn[CONNECTION_INTERFACE_CONTACTS].GetContactAttributes(
            [handle],
            # assuming this is available is technically wrong
            [ CONNECTION_INTERFACE_ALIASING ],
            False,
            reply_handler=self._get_contact_attributes_cb,
            error_handler=error)

    def _release_channel(self):
        # Finished with critical tasks.
        self.ready_handler(self)

    def _connect_to_signals(self):
        # Connect to signals
        self.signals.append(self[CHANNEL].connect_to_signal('Closed', 
                self._channel_closed_cb))

    # Called when channel proxy becomes ready. Chains method calls so actions
    # which depend on each other are executed in order.
    def _channel_ready(self, channel):
        self._target_id = self.properties[CHANNEL + '.TargetID']
        
        # Get contact attribute interfaces
        self[dbus.PROPERTIES_IFACE].Get(CHANNEL,
                'Requested',
                reply_handler=self._get_requested_cb,
                error_handler=error)

    # This is necessary so our signal isn't sent over D-Bus
    def do_closed(self):
        pass
gobject.type_register(ZChannel)

class ZTextChannel(ZChannel):
    def __init__(self, account_path, connection, path, properties, ready_handler):
        ZChannel.__init__(self, account_path, connection, path, properties, ready_handler)

        self._subject = None

    def __repr__(self):
        return "ZTextChannel(%s)" % self.object_path

    def _release_channel(self):
        # Finished with critical tasks.
        self.ready_handler(self)

        # Report to zeitgeist
        if not self._subject:
            self._subject = [Subject.new_for_values(
                uri = self._target_id,
                interpretation = unicode(Interpretation.IMMESSAGE),
                manifestation = unicode(Manifestation.SOFTWARE_SERVICE),
                origin = self.account_path,
                mimetype = "text/plain",
                text = self._target_alias)]

        if self._channel_requested:
            manifestation = unicode(Manifestation.USER_ACTIVITY)
        else:
            manifestation = unicode(Manifestation.WORLD_ACTIVITY)

        timestamp = int(time() * 1000)

        event = Event.new_for_values(
                timestamp = timestamp,
                interpretation = unicode(Interpretation.ACCESS_EVENT),
                manifestation = manifestation,
                actor = self.account_path,
                subjects = self._subject)
        zclient.insert_event(event)

    def _channel_closed_cb(self):
        for signal in self.signals:
            signal.remove()

        timestamp = int(time() * 1000)

        event = Event.new_for_values(
                timestamp = timestamp,
                interpretation = unicode(Interpretation.LEAVE_EVENT),
                manifestation = unicode(Manifestation.USER_ACTIVITY),
                actor = self.account_path,
                subjects = self._subject)
        zclient.insert_event(event)

        self.emit('closed')

    def _get_pending_messages_cb(self, messages):
        for message in messages:
            self._message_received_cb(*message)
            
        self._release_channel()

    def _default_operations_finished(self):
        self[CHANNEL_TYPE_TEXT].ListPendingMessages(
                False,
                reply_handler=self._get_pending_messages_cb,
                error_handler=error)

    def _message_received_cb(self, identification, timestamp, sender, contenttype,
            flags, content):
        logging.debug("Message received")
        if not self._subject:
            self._subject = [Subject.new_for_values(
                uri = self._target_id,
                interpretation = unicode(Interpretation.IMMESSAGE),
                manifestation = unicode(Manifestation.SOFTWARE_SERVICE),
                origin = self.account_path,
                mimetype = "text/plain",
                text = self._target_alias)]
        
        timestamp = timestamp * 1000

        event = Event.new_for_values(
                timestamp = timestamp,
                interpretation = unicode(Interpretation.RECEIVE_EVENT),
                manifestation = unicode(Manifestation.WORLD_ACTIVITY),
                actor = self.account_path,
                subjects = self._subject)
        zclient.insert_event(event)

    def _message_sent_cb(self, timestamp, contenttype, content):
        logging.debug("Message sent")

        timestamp = timestamp * 1000

        event = Event.new_for_values(
                timestamp = timestamp,
                interpretation = unicode(Interpretation.SEND_EVENT),
                manifestation = unicode(Manifestation.USER_ACTIVITY),
                actor = self.account_path,
                subjects = self._subject)
        zclient.insert_event(event)

    def _connect_to_signals(self):
        # Connect to signals
        self.signals.append(self[CHANNEL_TYPE_TEXT].connect_to_signal('Sent',
                self._message_sent_cb))
        self.signals.append(self[CHANNEL_TYPE_TEXT].connect_to_signal('Received',
                self._message_received_cb))
        self.signals.append(self[CHANNEL].connect_to_signal('Closed', 
                self._channel_closed_cb))

class ZStreamedMediaChannel(ZChannel):
    def __init__(self, account_path, connection, path, properties, ready_handler):
        self._audio_subject = None
        self._video_subject = None

        self.stream_cache = {}

        ZChannel.__init__(self, account_path, connection, path, properties, ready_handler)

    def __repr__(self):
        return "ZStreamedMediaChannel(%s)" % self.object_path

    def _channel_closed_cb(self):
        for signal in self.signals:
            signal.remove()

        self.emit('closed')

    def _stream_added_cb(self, streamid, handle, streamtype):
        logging.debug("Stream added. Streamtype: " + str(streamtype))
        self.stream_cache[streamid] = {'handle': handle, 'streamtype': streamtype}

        if not self._audio_subject:
            self._audio_subject = [Subject.new_for_values(
                uri = self._target_id,
                interpretation = unicode(Interpretation.AUDIO),
                manifestation = unicode(Manifestation.MEDIA_STREAM),
                origin = self.account_path,
                mimetype = "text/plain",
                text = self._target_alias)]

        if not self._video_subject:
            self._video_subject = [Subject.new_for_values(
                uri = self._target_id,
                interpretation = unicode(Interpretation.VIDEO),
                manifestation = unicode(Manifestation.MEDIA_STREAM),
                origin = self.account_path,
                mimetype = "text/plain",
                text = self._target_alias)]

        if streamtype == 0:
            subject = self._audio_subject
        elif streamtype == 1:
            subject = self._video_subject

        if self._channel_requested:
            manifestation = unicode(Manifestation.USER_ACTIVITY)
        else:
            manifestation = unicode(Manifestation.WORLD_ACTIVITY)

        timestamp = int(time() * 1000)
        event = Event.new_for_values(
                timestamp = timestamp,
                interpretation = unicode(Interpretation.ACCESS_EVENT),
                manifestation = manifestation,
                actor = self.account_path,
                subjects = subject)
        zclient.insert_event(event)


    def _stream_removed_cb(self, streamid):
        streamtype = self.stream_cache[streamid]['streamtype']
        logging.debug("Stream removed. Streamtype: " + str(streamtype))

        if streamtype == 0:
            subject = self._audio_subject
        elif streamtype == 1:
            subject = self._video_subject

        timestamp = int(time() * 1000)
        event = Event.new_for_values(
                timestamp = timestamp,
                interpretation = unicode(Interpretation.LEAVE_EVENT),
                manifestation = unicode(Manifestation.USER_ACTIVITY),
                actor = self.account_path,
                subject = subject)
        zclient.insert_event(event)

        del self.stream_cache[streamid]

    def _list_streams_cb(self, streams):
        for stream in streams:
            self._stream_added_cb(stream[0], stream[1], stream[2])

    def _default_operations_finished(self):
        self._release_channel()

        self[CHANNEL_TYPE_STREAMED_MEDIA].ListStreams(
                reply_handler=self._list_streams_cb,
                error_handler=error)

    def _connect_to_signals(self):
        # Connect to signals
        self.signals.append(self[CHANNEL_TYPE_STREAMED_MEDIA].connect_to_signal('StreamAdded',
                self._stream_added_cb))
        self.signals.append(self[CHANNEL_TYPE_STREAMED_MEDIA].connect_to_signal('StreamRemoved',
                self._stream_removed_cb))
        self.signals.append(self[CHANNEL].connect_to_signal('Closed', 
                self._channel_closed_cb))

class ZObserver(telepathy.server.Observer,
                      telepathy.server.DBusProperties):
    """
    Extends telepathy.server.Observer, listening for events


    ZObserver listens for a channel matching the filter is opened by telepathy,
    and reacts by opening connection and channel proxies in order to liisten in
    on events in the channel.
    """

    def __init__(self, client_name, enable_stream_observer=False,
            enable_text_observer=False):

        service_name = '.'.join ([CLIENT, client_name])
        object_path = '/' + service_name.replace('.', '/')

        bus_name = dbus.service.BusName(service_name, bus=dbus.SessionBus())

        telepathy.server.Observer.__init__(self, bus_name, object_path)
        telepathy.server.DBusProperties.__init__(self)

        self._implement_property_get(CLIENT, {
            'Interfaces': lambda: [ CLIENT_OBSERVER ],
          })


        filter_array = dbus.Array([], signature='a{sv}')

        if enable_stream_observer:
            filter_array.append(dbus.Dictionary({
                            CHANNEL + '.ChannelType': CHANNEL_TYPE_STREAMED_MEDIA,
                            CHANNEL + '.TargetHandleType': HANDLE_TYPE_CONTACT
                            }, signature='sv'))

        if enable_text_observer:
            filter_array.append(dbus.Dictionary({
                            CHANNEL + '.ChannelType': CHANNEL_TYPE_TEXT,
                            CHANNEL + '.TargetHandleType': HANDLE_TYPE_CONTACT
                            }, signature='sv'))

        self._implement_property_get(CLIENT_OBSERVER, {
            'ObserverChannelFilter': lambda: filter_array})

        self.connection_cache = {}
        self.channel_cache = {} 

    # Set async callbacks so ObserveChannels won't return until we're finished
    @dbus.service.method(CLIENT_OBSERVER,
        in_signature='ooa(oa{sv})oaoa{sv}', out_signature='',
        async_callbacks=('_success', '_error'))
    def ObserveChannels(self, account, conn, channels, dispatch_operation, 
            requests_satisfied, observer_info, _success, _error):

        # List of channels we're waiting to finish before we release the bus
        # with _success()
        pending_channels = []

        # Create ZChannel objects for the current connection
        def create_channels(conn):
            for path, properties in channels:
                if path not in self.channel_cache:
                    chantype = properties[CHANNEL + '.ChannelType']
                    if chantype == CHANNEL_TYPE_STREAMED_MEDIA:
                        chan = ZStreamedMediaChannel(account, conn, path, \
                                    properties, channel_ready)
                    elif chantype == CHANNEL_TYPE_TEXT:
                        chan =  ZTextChannel(account, conn, path, \
                                        properties, channel_ready)

                    pending_channels.append(chan)
                    self.channel_cache[path] = chan


        # Called when the channel proxy is invalidated
        def channel_closed(chan):
            try: 
                del self.channel_cache[chan.object_path]
                logging.debug("Channel closed: %s" % chan)
            except:
                logging.error("Couldn't delete channel: %s" % chan)

            # No more channels means we aren't needed. 
            # Telepathy will restart us when we are
            if not self.channel_cache:
                logging.warning("No channels left in list. Exiting")
                sys.exit()

        # Called when ZChannel object has finished its tasks
        # Removes channel from pending queue, and releases the connection 
        # if all channeled have been processed
        def channel_ready(chan):
            logging.debug("Channel ready: %s" % chan)

            pending_channels.remove(chan)
            chan.connect('closed', channel_closed)

            if not pending_channels:
                _success()

        # Called when the connection proxy is invalidated
        def connection_closed(conn):
            logging.debug("Connection closed: %s" % conn)
            del self.connection_cache[conn.object_path]

        # Called when ZConnection object has finished its tasks
        # Connects to 'disconnected' signal to listen for connection
        # invalidation. Triggers creation of ZChannel objects for the
        # connection
        def connection_ready(conn):
            logging.debug("Connection ready: %s" % conn)
            conn.connect('disconnected', connection_closed)
            create_channels(conn)

        # If the connection exists in cache, call the handler manually to
        # set up channels. Otherwise, create the connection and cache it.
        if conn not in self.connection_cache:
            try:
                logging.debug("Trying to create connection...")
                self.connection_cache[conn] = ZConnection(conn, connection_ready)
            except:
                logging.error("Connection creation failed")
        else:
            logging.debug("Connection exists: %s" % conn)
            create_channels(self.connection_cache[conn])

def main():
    ZObserver("Zeitgeist", enable_stream_observer=True,
            enable_text_observer=True)

if __name__ == '__main__':
    gobject.timeout_add(0, main)
    loop = gobject.MainLoop()
    loop.run()
