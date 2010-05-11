#include "nsIGenericFactory.h"
#include "zeitgeist.h"
#include "zeitgeistextend.h"

NS_GENERIC_FACTORY_CONSTRUCTOR(zeitgeistextend)

static nsModuleComponentInfo components[] =
{
  {
    ZEITGEIST_COMPONENT_CLASSNAME,
    ZEITGEIST_COMPONENT_CID,
    ZEITGEIST_COMPONENT_CONTRACTID,
    zeitgeistextendConstructor,
  }
};

NS_IMPL_NSGETMODULE("ZeitgeistModule", components)
