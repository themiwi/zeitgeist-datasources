AC_INIT([zeitgeist-dataproviders],
	[0.1.0],
	[https://bugs.launchpad.net/zeitgeist-dataproviders/])

AM_INIT_AUTOMAKE([1.9 foreign])

dnl pkg-config
AC_PATH_PROG(PKG_CONFIG, pkg-config, no)
if test "x$PKG_CONFIG" = "xno"; then
	AC_MSG_ERROR([You need to install pkg-config])
fi

AC_PROG_INSTALL
AC_PROG_CC
AC_PROG_CXX
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
dnl Enable building only supported plugins
dnl ==============================================
AC_ARG_ENABLE([all-plugins],
	[AS_HELP_STRING([--enable-all-plugins],[Enable building of all plugins without checking for their support])],
        [all_plugins=$enableval], [all_plugins=no])

AC_MSG_RESULT($all_plugins)

# The full list of plugins
allowed_plugins="bzr chrome eog firefox-libzg geany gedit npapi-plugin rhythmbox totem-libzg"
# currently disabled = "epiphany tomboy"

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
			#PKG_CHECK_MODULES()
		;;
		eog)
		;;
		epiphany)
			# not supported atm
			add_plugin="0"
		;;
		firefox-libzg)
		;;
		geany)
			PKG_CHECK_MODULES(GEANY, geany,
				[HAVE_GEANY=yes], [HAVE_GEANY=no])
			if test "${HAVE_GEANY}" != "yes" ; then
				plugin_error_or_ignore "geany not found"
				add_plugin="0"
			fi
		;;
		gedit)
		;;
		npapi-plugin)
		;;
		rhythmbox)
		;;
		tomboy)
		;;
		totem-libzg)
			if test "${with_vala}" != "yes" ; then
				plugin_error_or_ignore "you need vala installed to use the ${plugin} plugin"
				add_plugin="0"
			else
				PKG_CHECK_MODULES(TOTEM_PLPARSER, totem-plparser,
					[HAVE_TOTEM_PLPARSER=yes], [HAVE_TOTEM_PLPARSER=no])
				if test "${HAVE_TOTEM_PLPARSER}" != "yes" ; then
					plugin_error_or_ignore "totem-plparser package not found"
					add_plugin="0"
				fi
			fi
		;;
        esac

	# Add the specified plugin
	if test "${add_plugin}" = "1" ; then
		used_plugins2="${used_plugins2} ${plugin}"
	fi
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
chrome/Makefile
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
 
