package: 
	#logo
	(cd src && find . \( -iname "*.pyc" -or -iname ".*.swp" \) -delete && \
	zip -r ../Zeitgeist-nightly.xpi chrome chrome.manifest defaults/ install.rdf)

package_upstream: clean
	#~ version = $(shell xpath -q -e '/RDF/Description/em:version/text()' src/install.rdf); \
	tar czf ../zeitgeist-firefox-extension_$(shell xpath -q -e '/RDF/Description/em:version/text()' src/install.rdf).orig.tar.gz *


#logo: src/chrome/content/logo.png

#~ src/chrome/content/logo.png: logo.svg
	#~ rsvg-convert logo.svg -o src/chrome/content/logo.png --width=32 --keep-aspect-ratio --format=png

.PHONY: package clean
clean:
	rm -rf `bzr ls --ignored --unknown -R`
	
symlink_zeitgeist:
	#check if for the zeitgeist modul
	#if python -c "from zeitgeist.dbusutils import DBusInterface" fails get the source and link it into
	# src/chrome(content)
	if ! (cd src/chrome/content && python -c "from zeitgeist.dbusutils import DBusInterface") >/dev/null 2>&1; \
		then \
			rm -rf zeitgeist-tmp; \
			bzr get lp:zeitgeist zeitgeist-tmp; \
			cd src/chrome/content ; \
			rm -f zeitgeist; \
			ln -s ../../../zeitgeist-tmp/zeitgeist .; \
	fi
	
moz_profile:
	# if .moz_profile exists get the profile dir from there
	# else search for ~/.mozilla/firefox/*.default
	if test ! -f .moz_profile -a -d ~/.mozilla/firefox/*.default/extensions; \
		then \
			echo `cd ~/.mozilla/firefox/*.default && pwd` > .moz_profile; \
	fi
	
register_ext: moz_profile
	value=`cat .moz_profile`; \
	if test -n "$$value" -a -d $$value; \
		then \
			echo `cd src && pwd` > $$value/extensions/zeitgeist@zeitgeist-project.com; \
	fi
	
devel: symlink_zeitgeist register_ext
	
