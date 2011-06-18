/*
 * DO NOT EDIT.  THIS FILE IS GENERATED FROM zeitgeist.idl
 */

#ifndef __gen_zeitgeist_h__
#define __gen_zeitgeist_h__


#ifndef __gen_nsISupports_h__
#include "nsISupports.h"
#endif

/* For IDL files that don't want to include root IDL files. */
#ifndef NS_NO_VTABLE
#define NS_NO_VTABLE
#endif

/* starting interface:    zeitgeist */
#define ZEITGEIST_IID_STR "d879c08c-517d-44f0-83e1-3ef75a527ddf"

#define ZEITGEIST_IID \
  {0xd879c08c, 0x517d, 0x44f0, \
    { 0x83, 0xe1, 0x3e, 0xf7, 0x5a, 0x52, 0x7d, 0xdf }}

class NS_NO_VTABLE NS_SCRIPTABLE zeitgeist : public nsISupports {
 public: 

  NS_DECLARE_STATIC_IID_ACCESSOR(ZEITGEIST_IID)

  /* void insert (in string url, in string mimetype, in AUTF8String title, in string origin); */
  NS_SCRIPTABLE NS_IMETHOD Insert(const char *url, const char *mimetype, const nsACString & title, const char *origin) = 0;

};

  NS_DEFINE_STATIC_IID_ACCESSOR(zeitgeist, ZEITGEIST_IID)

/* Use this macro when declaring classes that implement this interface. */
#define NS_DECL_ZEITGEIST \
  NS_SCRIPTABLE NS_IMETHOD Insert(const char *url, const char *mimetype, const nsACString & title, const char *origin); 

/* Use this macro to declare functions that forward the behavior of this interface to another object. */
#define NS_FORWARD_ZEITGEIST(_to) \
  NS_SCRIPTABLE NS_IMETHOD Insert(const char *url, const char *mimetype, const nsACString & title, const char *origin) { return _to Insert(url, mimetype, title, origin); } 

/* Use this macro to declare functions that forward the behavior of this interface to another object in a safe way. */
#define NS_FORWARD_SAFE_ZEITGEIST(_to) \
  NS_SCRIPTABLE NS_IMETHOD Insert(const char *url, const char *mimetype, const nsACString & title, const char *origin) { return !_to ? NS_ERROR_NULL_POINTER : _to->Insert(url, mimetype, title, origin); } 

#if 0
/* Use the code below as a template for the implementation class for this interface. */

/* Header file */
class _MYCLASS_ : public zeitgeist
{
public:
  NS_DECL_ISUPPORTS
  NS_DECL_ZEITGEIST

  _MYCLASS_();

private:
  ~_MYCLASS_();

protected:
  /* additional members */
};

/* Implementation file */
NS_IMPL_ISUPPORTS1(_MYCLASS_, zeitgeist)

_MYCLASS_::_MYCLASS_()
{
  /* member initializers and constructor code */
}

_MYCLASS_::~_MYCLASS_()
{
  /* destructor code */
}

/* void insert (in string url, in string mimetype, in AUTF8String title, in string origin); */
NS_IMETHODIMP _MYCLASS_::Insert(const char *url, const char *mimetype, const nsACString & title, const char *origin)
{
    return NS_ERROR_NOT_IMPLEMENTED;
}

/* End of implementation class template. */
#endif


#endif /* __gen_zeitgeist_h__ */
