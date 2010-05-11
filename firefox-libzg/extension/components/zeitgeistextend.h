#ifndef _ZEITGEISTEXTEND_H_
#define _ZEITGEISTEXTEND_H_

#include "zeitgeist.h"
#include <zeitgeist.h>

#define ZEITGEIST_COMPONENT_CONTRACTID "@zeitgeist-project.com/DATAPROVIDER/firefox-xpcom;1"
#define ZEITGEIST_COMPONENT_CLASSNAME "zeitgeist dataprovider for firefox"
#define ZEITGEIST_COMPONENT_CID  { 0xd879c08c, 0x517d, 0x44f0, { 0x83, 0xe1, 0x3e, 0xf7, 0x5a, 0x52, 0x7d, 0xdf } }

//d879c08c-517d-44f0-83e1-3ef75a527ddf
class zeitgeistextend : public zeitgeist
{
	public:
		NS_DECL_ISUPPORTS
		NS_DECL_ZEITGEIST

		zeitgeistextend();
		virtual ~zeitgeistextend();
		ZeitgeistLog	*log;
	
};
#endif
