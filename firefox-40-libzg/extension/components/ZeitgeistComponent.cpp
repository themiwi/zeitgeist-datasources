/*
 * ZeitgeistComponent.cpp
 * This file is part of zeitgeist dataprovider for firefox 
 *
 * Copyright (C) 2010 - Markus Korn <thekorn@gmx.de>
 *
 * zeitgeist dataprovider for firefox is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 * 
 * zeitgeist dataprovider for firefox is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
 
 
#include "mozilla/ModuleUtils.h"
#include "zeitgeist.h"
#include "zeitgeistextend.h"

NS_GENERIC_FACTORY_CONSTRUCTOR(zeitgeistextend)

NS_DEFINE_NAMED_CID(ZEITGEIST_COMPONENT_CID);

static const mozilla::Module::CIDEntry kZeitgeistCIDs[] = {
  { &kZEITGEIST_COMPONENT_CID, false, NULL, zeitgeistextendConstructor },
  { NULL }
};

static const mozilla::Module::ContractIDEntry kZeitgeistContracts[] = {
  { ZEITGEIST_COMPONENT_CONTRACTID, &kZEITGEIST_COMPONENT_CID },
  { NULL }
};

static const mozilla::Module kZeitgeistModule = {
  mozilla::Module::kVersion,
  kZeitgeistCIDs,
  kZeitgeistContracts,
  NULL
};

NSMODULE_DEFN(ZeitgeistModule) = &kZeitgeistModule;

NS_IMPL_MOZILLA192_NSGETMODULE(&kZeitgeistModule)
