

/* this ALWAYS GENERATED file contains the definitions for the interfaces */


 /* File created by MIDL compiler version 7.00.0416 */
/* Compiler settings for wmnetsourcecreator.idl:
    Oicf, W1, Zp8, env=Win32 (32b run)
    protocol : dce , ms_ext, c_ext, robust
    error checks: allocation ref bounds_check enum stub_data 
    VC __declspec() decoration level: 
         __declspec(uuid()), __declspec(selectany), __declspec(novtable)
         DECLSPEC_UUID(), MIDL_INTERFACE()
*/
//@@MIDL_FILE_HEADING(  )

#pragma warning( disable: 4049 )  /* more than 64k source lines */


/* verify that the <rpcndr.h> version is high enough to compile this file*/
#ifndef __REQUIRED_RPCNDR_H_VERSION__
#define __REQUIRED_RPCNDR_H_VERSION__ 475
#endif

#include "rpc.h"
#include "rpcndr.h"

#ifndef __RPCNDR_H_VERSION__
#error this stub requires an updated version of <rpcndr.h>
#endif // __RPCNDR_H_VERSION__

#ifndef COM_NO_WINDOWS_H
#include "windows.h"
#include "ole2.h"
#endif /*COM_NO_WINDOWS_H*/

#ifndef __wmnetsourcecreator_h__
#define __wmnetsourcecreator_h__

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

/* Forward Declarations */ 

#ifndef __INSNetSourceCreator_FWD_DEFINED__
#define __INSNetSourceCreator_FWD_DEFINED__
typedef interface INSNetSourceCreator INSNetSourceCreator;
#endif 	/* __INSNetSourceCreator_FWD_DEFINED__ */


/* header files for imported files */
#include "oaidl.h"

#ifdef __cplusplus
extern "C"{
#endif 

void * __RPC_USER MIDL_user_allocate(size_t);
void __RPC_USER MIDL_user_free( void * ); 

/* interface __MIDL_itf_wmnetsourcecreator_0000 */
/* [local] */ 

//+-------------------------------------------------------------------------
//
//  Microsoft Windows Media
//  Copyright (C) Microsoft Corporation. All rights reserved
//
//  Automatically generated by Midl from WMNetSourceCreator.idl
//
// DO NOT EDIT THIS FILE.
//
//--------------------------------------------------------------------------
EXTERN_GUID( CLSID_ClientNetManager, 0xCD12A3CE,0x9C42,0x11D2,0xBE,0xED,0x00,0x60,0x08,0x2F,0x20,0x54  );
EXTERN_GUID( IID_INSNetSourceCreator, 0x0C0E4080,0x9081,0x11d2,0xBE,0xEC,0x00,0x60,0x08,0x2F,0x20,0x54  );

typedef unsigned __int64 QWORD;



extern RPC_IF_HANDLE __MIDL_itf_wmnetsourcecreator_0000_v0_0_c_ifspec;
extern RPC_IF_HANDLE __MIDL_itf_wmnetsourcecreator_0000_v0_0_s_ifspec;

#ifndef __INSNetSourceCreator_INTERFACE_DEFINED__
#define __INSNetSourceCreator_INTERFACE_DEFINED__

/* interface INSNetSourceCreator */
/* [unique][version][uuid][object] */ 


EXTERN_C const IID IID_INSNetSourceCreator;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    MIDL_INTERFACE("0C0E4080-9081-11d2-BEEC-0060082F2054")
    INSNetSourceCreator : public IUnknown
    {
    public:
        virtual HRESULT STDMETHODCALLTYPE Initialize( void) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE CreateNetSource( 
            /* [in] */ LPCWSTR pszStreamName,
            /* [in] */ IUnknown *pMonitor,
            /* [in] */ BYTE *pData,
            /* [in] */ IUnknown *pUserContext,
            /* [in] */ IUnknown *pCallback,
            /* [in] */ QWORD qwContext) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetNetSourceProperties( 
            /* [in] */ LPCWSTR pszStreamName,
            /* [out] */ IUnknown **ppPropertiesNode) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetNetSourceSharedNamespace( 
            /* [out] */ IUnknown **ppSharedNamespace) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetNetSourceAdminInterface( 
            /* [in] */ LPCWSTR pszStreamName,
            /* [out] */ VARIANT *pVal) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetNumProtocolsSupported( 
            /* [out] */ DWORD *pcProtocols) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE GetProtocolName( 
            /* [in] */ DWORD dwProtocolNum,
            /* [out] */ WCHAR *pwszProtocolName,
            /* [out][in] */ WORD *pcchProtocolName) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE Shutdown( void) = 0;
        
    };
    
#else 	/* C style interface */

    typedef struct INSNetSourceCreatorVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE *QueryInterface )( 
            INSNetSourceCreator * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ void **ppvObject);
        
        ULONG ( STDMETHODCALLTYPE *AddRef )( 
            INSNetSourceCreator * This);
        
        ULONG ( STDMETHODCALLTYPE *Release )( 
            INSNetSourceCreator * This);
        
        HRESULT ( STDMETHODCALLTYPE *Initialize )( 
            INSNetSourceCreator * This);
        
        HRESULT ( STDMETHODCALLTYPE *CreateNetSource )( 
            INSNetSourceCreator * This,
            /* [in] */ LPCWSTR pszStreamName,
            /* [in] */ IUnknown *pMonitor,
            /* [in] */ BYTE *pData,
            /* [in] */ IUnknown *pUserContext,
            /* [in] */ IUnknown *pCallback,
            /* [in] */ QWORD qwContext);
        
        HRESULT ( STDMETHODCALLTYPE *GetNetSourceProperties )( 
            INSNetSourceCreator * This,
            /* [in] */ LPCWSTR pszStreamName,
            /* [out] */ IUnknown **ppPropertiesNode);
        
        HRESULT ( STDMETHODCALLTYPE *GetNetSourceSharedNamespace )( 
            INSNetSourceCreator * This,
            /* [out] */ IUnknown **ppSharedNamespace);
        
        HRESULT ( STDMETHODCALLTYPE *GetNetSourceAdminInterface )( 
            INSNetSourceCreator * This,
            /* [in] */ LPCWSTR pszStreamName,
            /* [out] */ VARIANT *pVal);
        
        HRESULT ( STDMETHODCALLTYPE *GetNumProtocolsSupported )( 
            INSNetSourceCreator * This,
            /* [out] */ DWORD *pcProtocols);
        
        HRESULT ( STDMETHODCALLTYPE *GetProtocolName )( 
            INSNetSourceCreator * This,
            /* [in] */ DWORD dwProtocolNum,
            /* [out] */ WCHAR *pwszProtocolName,
            /* [out][in] */ WORD *pcchProtocolName);
        
        HRESULT ( STDMETHODCALLTYPE *Shutdown )( 
            INSNetSourceCreator * This);
        
        END_INTERFACE
    } INSNetSourceCreatorVtbl;

    interface INSNetSourceCreator
    {
        CONST_VTBL struct INSNetSourceCreatorVtbl *lpVtbl;
    };

    

#ifdef COBJMACROS


#define INSNetSourceCreator_QueryInterface(This,riid,ppvObject)	\
    ( (This)->lpVtbl -> QueryInterface(This,riid,ppvObject) ) 

#define INSNetSourceCreator_AddRef(This)	\
    ( (This)->lpVtbl -> AddRef(This) ) 

#define INSNetSourceCreator_Release(This)	\
    ( (This)->lpVtbl -> Release(This) ) 


#define INSNetSourceCreator_Initialize(This)	\
    ( (This)->lpVtbl -> Initialize(This) ) 

#define INSNetSourceCreator_CreateNetSource(This,pszStreamName,pMonitor,pData,pUserContext,pCallback,qwContext)	\
    ( (This)->lpVtbl -> CreateNetSource(This,pszStreamName,pMonitor,pData,pUserContext,pCallback,qwContext) ) 

#define INSNetSourceCreator_GetNetSourceProperties(This,pszStreamName,ppPropertiesNode)	\
    ( (This)->lpVtbl -> GetNetSourceProperties(This,pszStreamName,ppPropertiesNode) ) 

#define INSNetSourceCreator_GetNetSourceSharedNamespace(This,ppSharedNamespace)	\
    ( (This)->lpVtbl -> GetNetSourceSharedNamespace(This,ppSharedNamespace) ) 

#define INSNetSourceCreator_GetNetSourceAdminInterface(This,pszStreamName,pVal)	\
    ( (This)->lpVtbl -> GetNetSourceAdminInterface(This,pszStreamName,pVal) ) 

#define INSNetSourceCreator_GetNumProtocolsSupported(This,pcProtocols)	\
    ( (This)->lpVtbl -> GetNumProtocolsSupported(This,pcProtocols) ) 

#define INSNetSourceCreator_GetProtocolName(This,dwProtocolNum,pwszProtocolName,pcchProtocolName)	\
    ( (This)->lpVtbl -> GetProtocolName(This,dwProtocolNum,pwszProtocolName,pcchProtocolName) ) 

#define INSNetSourceCreator_Shutdown(This)	\
    ( (This)->lpVtbl -> Shutdown(This) ) 

#endif /* COBJMACROS */


#endif 	/* C style interface */



HRESULT STDMETHODCALLTYPE INSNetSourceCreator_Initialize_Proxy( 
    INSNetSourceCreator * This);


void __RPC_STUB INSNetSourceCreator_Initialize_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_CreateNetSource_Proxy( 
    INSNetSourceCreator * This,
    /* [in] */ LPCWSTR pszStreamName,
    /* [in] */ IUnknown *pMonitor,
    /* [in] */ BYTE *pData,
    /* [in] */ IUnknown *pUserContext,
    /* [in] */ IUnknown *pCallback,
    /* [in] */ QWORD qwContext);


void __RPC_STUB INSNetSourceCreator_CreateNetSource_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_GetNetSourceProperties_Proxy( 
    INSNetSourceCreator * This,
    /* [in] */ LPCWSTR pszStreamName,
    /* [out] */ IUnknown **ppPropertiesNode);


void __RPC_STUB INSNetSourceCreator_GetNetSourceProperties_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_GetNetSourceSharedNamespace_Proxy( 
    INSNetSourceCreator * This,
    /* [out] */ IUnknown **ppSharedNamespace);


void __RPC_STUB INSNetSourceCreator_GetNetSourceSharedNamespace_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_GetNetSourceAdminInterface_Proxy( 
    INSNetSourceCreator * This,
    /* [in] */ LPCWSTR pszStreamName,
    /* [out] */ VARIANT *pVal);


void __RPC_STUB INSNetSourceCreator_GetNetSourceAdminInterface_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_GetNumProtocolsSupported_Proxy( 
    INSNetSourceCreator * This,
    /* [out] */ DWORD *pcProtocols);


void __RPC_STUB INSNetSourceCreator_GetNumProtocolsSupported_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_GetProtocolName_Proxy( 
    INSNetSourceCreator * This,
    /* [in] */ DWORD dwProtocolNum,
    /* [out] */ WCHAR *pwszProtocolName,
    /* [out][in] */ WORD *pcchProtocolName);


void __RPC_STUB INSNetSourceCreator_GetProtocolName_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);


HRESULT STDMETHODCALLTYPE INSNetSourceCreator_Shutdown_Proxy( 
    INSNetSourceCreator * This);


void __RPC_STUB INSNetSourceCreator_Shutdown_Stub(
    IRpcStubBuffer *This,
    IRpcChannelBuffer *_pRpcChannelBuffer,
    PRPC_MESSAGE _pRpcMessage,
    DWORD *_pdwStubPhase);



#endif 	/* __INSNetSourceCreator_INTERFACE_DEFINED__ */


/* Additional Prototypes for ALL interfaces */

unsigned long             __RPC_USER  VARIANT_UserSize(     unsigned long *, unsigned long            , VARIANT * ); 
unsigned char * __RPC_USER  VARIANT_UserMarshal(  unsigned long *, unsigned char *, VARIANT * ); 
unsigned char * __RPC_USER  VARIANT_UserUnmarshal(unsigned long *, unsigned char *, VARIANT * ); 
void                      __RPC_USER  VARIANT_UserFree(     unsigned long *, VARIANT * ); 

/* end of Additional Prototypes */

#ifdef __cplusplus
}
#endif

#endif



