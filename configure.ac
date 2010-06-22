AC_INIT([zeitgeist-dataproviders],
	[0.1.0],
	[https://bugs.launchpad.net/zeitgeist-dataproviders/])

AC_PREFIX_DEFAULT([/usr])

AM_INIT_AUTOMAKE([1.9 foreign])

# Enable silent build when available (Automake 1.11)
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])

dnl pkg-config
AC_PATH_PROG(PKG_CONFIG, pkg-config, no)
if test "x$PKG_CONFIG" = "xno"; then
	AC_MSG_ERROR([You need to install pkg-config])
fi

AC_PROG_INSTALL
AC_PROG_CC
AC_PROG_CXX
AC_PROG_LIBTOOL
AC_STDC_HEADERS

dnl ==============================================
dnl Check for vala
dnl ==============================================
AC_ARG_WITH([vala],
	AS_HELP_STRING([--without-vala],
		[Disables Vala plugins]),
	[],[with_vala=yes])

if test "$with_vala" != "no"; then
  AM_PROG_VALAC([0.7.10])
fi
AM_CONDITIONAL(ENABLE_VALA, test "x$with_vala" = "xyes")

dnl ==============================================
dnl Check commonly used packages
dnl ==============================================

PKG_CHECK_MODULES(ZEITGEIST, zeitgeist-1.0, [HAVE_LIBZG=yes], [HAVE_LIBZG=no])
PKG_CHECK_MODULES(GTK, gtk+-2.0, [HAVE_GTK=yes], [HAVE_GTK=no])

dnl ==============================================
dnl Enable building only supported plugins
dnl ==============================================
AC_ARG_ENABLE([all-plugins],
	[AS_HELP_STRING([--enable-all-plugins],[Enable building of all plugins without checking for their support])],
        [all_plugins=$enableval], [all_plugins=no])

AC_MSG_RESULT($all_plugins)

# The full list of plugins
allowed_plugins="bzr chrome eog firefox-libzg geany gedit rhythmbox rhythmbox-popular totem-libzg totem-recent"
# currently disabled = "epiphany tomboy"

# npapi-plugin has a template Makefile.am, but don't use it directly
#   - see chrome's Makefile.am for how to compile it

plugin_error_or_ignore()
{
	if test "${error_on_bad_plugin}" = "1" ; then
		AC_MSG_ERROR([$1])
	else
		AC_MSG_WARN([$1 (disabling plugin)])
	fi
}

used_plugins="${allowed_plugins}"
used_plugins2=""
if test "x${all_plugins}" = "xyes" ; then
	error_on_bad_plugin="1"
else
	error_on_bad_plugin="0"
fi

# Check for plugin-specific requirements and error if necessary
for plugin in ${used_plugins}; do
	add_plugin="1"

	case ${plugin} in
		bzr)
		;;
		chrome)
			if test "${HAVE_LIBZG}" != "yes" ; then
				plugin_error_or_ignore "libzeitgeist not found"
				continue
			fi
		;;
		eog)
		;;
		epiphany)
			# not supported atm
			continue
		;;
		firefox-libzg)
			if test "${HAVE_LIBZG}" != "yes" ; then
				plugin_error_or_ignore "libzeitgeist not found"
				continue
			fi
			PKG_CHECK_MODULES(LIBXUL, libxul,
				[HAVE_LIBXUL=yes], [HAVE_LIBXUL=no])
			if test "${HAVE_LIBXUL}" != "yes" ; then
				plugin_error_or_ignore "libxul not found"
				continue
			fi
			XPIDL_BIN="`$PKG_CONFIG --variable=sdkdir libxul`/bin/xpidl"
			AC_SUBST(XPIDL_BIN)
			XUL_IDLDIR="`$PKG_CONFIG --variable=idldir libxul`"
			AC_SUBST(XUL_IDLDIR)
		;;
		geany)
			if test "${HAVE_LIBZG}" != "yes" ; then
				plugin_error_or_ignore "libzeitgeist not found"
				continue
			fi
			PKG_CHECK_MODULES(GEANY, geany,
				[HAVE_GEANY=yes], [HAVE_GEANY=no])
			if test "${HAVE_GEANY}" != "yes" ; then
				plugin_error_or_ignore "geany not found"
				continue
			fi
		;;
		gedit)
		;;
		npapi-plugin)
			if test "${HAVE_LIBZG}" != "yes" ; then
				plugin_error_or_ignore "libzeitgeist not found"
				continue
			fi
		;;
		rhythmbox)
		;;
		rhythmbox-popular)
			if test "${with_vala}" != "yes" ; then
				plugin_error_or_ignore "you need vala installed to use the ${plugin} plugin"
				continue
			fi
			if test "${HAVE_LIBZG}" != "yes" ; then
				plugin_error_or_ignore "libzeitgeist not found"
				continue
			fi
			if test "${HAVE_GTK}" != "yes" ; then
				plugin_error_or_ignore "gtk+-2.0 not found"
				continue
			fi
			PKG_CHECK_MODULES([LIBXML], [libxml-2.0],
				[HAVE_LIBXML=yes], [HAVE_LIBXML=no])
			if test "${HAVE_LIBXML}" != "yes" ; then
				plugin_error_or_ignore "libxml package not found"
				continue
			fi
		;;
		tomboy)
			# not supported atm
			continue
		;;
		totem*)
			if test "${with_vala}" != "yes" ; then
				plugin_error_or_ignore "you need vala installed to use the ${plugin} plugin"
				continue
			fi
			if test "${HAVE_LIBZG}" != "yes" ; then
				plugin_error_or_ignore "libzeitgeist not found"
				continue
			fi
			if test "${HAVE_GTK}" != "yes" ; then
				plugin_error_or_ignore "gtk+-2.0 not found"
				continue
			fi
			PKG_CHECK_MODULES(TOTEM_PLPARSER, totem-plparser,
				[HAVE_TOTEM_PLPARSER=yes], [HAVE_TOTEM_PLPARSER=no])
			if test "${HAVE_TOTEM_PLPARSER}" != "yes" ; then
				plugin_error_or_ignore "totem-plparser package not found"
				continue
			fi
		;;
		*)
			plugin_error_or_ignore "${plugin} is not handled"
			continue
		;;
        esac

	# Add the specified plugin
	used_plugins2="${used_plugins2} ${plugin}"
done

ALL_PLUGINS=$allowed_plugins
PLUGINS=$used_plugins2

AC_MSG_CHECKING([which plugins to compile])
AC_MSG_RESULT([$PLUGINS])

AC_SUBST([PLUGINS])

AC_SUBST([AM_CPPFLAGS])
AC_SUBST([AM_CFLAGS])
AC_SUBST([AM_CXXFLAGS])
AC_SUBST([AM_LDFLAGS])

AC_OUTPUT([
Makefile
bzr/Makefile
chrome/Makefile
eog/Makefile
firefox-libzg/Makefile
firefox-libzg/extension/Makefile
firefox-libzg/extension/components/Makefile
geany/Makefile
gedit/Makefile
rhythmbox/Makefile
rhythmbox-popular/Makefile
totem-libzg/Makefile
totem-recent/Makefile
])

AC_MSG_NOTICE([Zeitgeist-dataproviders was configured with the following options:])

if test "x${PLUGINS}" != "x" ; then
        for allowed_plugin in ${ALL_PLUGINS}; do
                for plugin in ${PLUGINS}; do
                        case ${allowed_plugin} in
                                ${plugin})
                                        AC_MSG_NOTICE([** ${allowed_plugin} plugin enabled])
                                        continue 2
                                ;;
                                *);;
                        esac
                done
                AC_MSG_NOTICE([   ${allowed_plugin} plugin disabled])
        done
else
        AC_MSG_NOTICE([   No plugins enabled])
fi
 
