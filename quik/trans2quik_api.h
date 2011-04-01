#pragma once

#ifdef TRANS2QUIK_EXPORTS
#define TRANS2QUIK_API __declspec (dllexport)
#pragma message ("TRANS2QUIK_API defined as __declspec (dllexport)")
#else
//#pragma message ("TRANS2QUIK_API defined as __declspec (dllimport)")
#define TRANS2QUIK_API __declspec (dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void (__stdcall *TRANS2QUIK_CONNECTION_STATUS_CALLBACK) (long nConnectionEvent, long nExtendedErrorCode, LPCSTR lpcstrInfoMessage);
typedef void (__stdcall *TRANS2QUIK_TRANSACTION_REPLY_CALLBACK) (long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, DWORD dwTransId, double dOrderNum, LPCSTR lpcstrTransactionReplyMessage);
typedef void (__stdcall *TRANS2QUIK_ORDER_STATUS_CALLBACK)      (long nMode, DWORD dwTransID, double dNumber, LPCSTR ClassCode, LPCSTR SecCode, double dPrice, long nBalance, double dValue, long nIsSell, long nStatus, long nOrderDescriptor);
typedef void (__stdcall *TRANS2QUIK_TRADE_STATUS_CALLBACK)      (long nMode, double dNumber, double dOrderNumber, LPCSTR ClassCode, LPCSTR SecCode, double dPrice, long nQty, double dValue, long nIsSell, long nTradeDescriptor);

//typedef void (__stdcall *TRANS2QUIK_CONNECTION_STATUS_CALLBACK) (long nConnectionEvent, long nExtendedErrorCode, LPSTR lpstrInfoMessage);
//typedef void (__stdcall *TRANS2QUIK_TRANSACTION_REPLY_CALLBACK) (long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, DWORD dwTransId, double dOrderNum, LPSTR lpstrTransactionReplyMessage);

#define TRANS2QUIK_SUCCESS						0
#define TRANS2QUIK_FAILED						1
#define TRANS2QUIK_QUIK_TERMINAL_NOT_FOUND		2
#define TRANS2QUIK_DLL_VERSION_NOT_SUPPORTED	3
#define TRANS2QUIK_ALREADY_CONNECTED_TO_QUIK	4
#define TRANS2QUIK_WRONG_SYNTAX					5
#define TRANS2QUIK_QUIK_NOT_CONNECTED			6
#define TRANS2QUIK_DLL_NOT_CONNECTED			7
#define TRANS2QUIK_QUIK_CONNECTED				8
#define TRANS2QUIK_QUIK_DISCONNECTED			9
#define TRANS2QUIK_DLL_CONNECTED				10
#define TRANS2QUIK_DLL_DISCONNECTED				11
#define TRANS2QUIK_MEMORY_ALLOCATION_ERROR		12
#define TRANS2QUIK_WRONG_CONNECTION_HANDLE		13
#define TRANS2QUIK_WRONG_INPUT_PARAMS			14


long TRANS2QUIK_API __stdcall TRANS2QUIK_SEND_SYNC_TRANSACTION (LPSTR lpstTransactionString, long* pnReplyCode, PDWORD pdwTransId, double* pdOrderNum, LPSTR lpstrResultMessage, DWORD dwResultMessageSize, long* pnExtendedErrorCode, LPSTR lpstErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_SEND_ASYNC_TRANSACTION (LPSTR lpstTransactionString, long* pnExtendedErrorCode, LPSTR lpstErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_CONNECT (LPSTR lpstConnectionParamsString, long* pnExtendedErrorCode, LPSTR lpstrErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_DISCONNECT (long* pnExtendedErrorCode, LPSTR lpstrErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_SET_CONNECTION_STATUS_CALLBACK (TRANS2QUIK_CONNECTION_STATUS_CALLBACK pfConnectionStatusCallback, long* pnExtendedErrorCode, LPSTR lpstrErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_SET_TRANSACTIONS_REPLY_CALLBACK (TRANS2QUIK_TRANSACTION_REPLY_CALLBACK pfTransactionReplyCallback, long* pnExtendedErrorCode, LPSTR lpstrErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_IS_QUIK_CONNECTED (long* pnExtendedErrorCode, LPSTR lpstrErrorMessage, DWORD dwErrorMessageSize);
long TRANS2QUIK_API __stdcall TRANS2QUIK_IS_DLL_CONNECTED (long* pnExtendedErrorCode, LPSTR lpstrErrorMessage, DWORD dwErrorMessageSize);

long TRANS2QUIK_API __stdcall TRANS2QUIK_SUBSCRIBE_ORDERS (LPSTR ClassCode, LPSTR Seccodes);
long TRANS2QUIK_API __stdcall TRANS2QUIK_UNSUBSCRIBE_ORDERS ();
long TRANS2QUIK_API __stdcall TRANS2QUIK_START_ORDERS (TRANS2QUIK_ORDER_STATUS_CALLBACK pfnOrderStatusCallback);

long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_QTY (long nOrderDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_DATE (long nOrderDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_TIME (long nOrderDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_ACTIVATION_TIME (long nOrderDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_WITHDRAW_TIME (long nOrderDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_EXPIRY (long nOrderDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_ACCRUED_INT (long nOrderDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_YIELD (long nOrderDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_UID (long nOrderDescriptor);

LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_USERID (long nOrderDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_ACCOUNT (long nOrderDescriptor); 
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_BROKERREF (long nOrderDescriptor); 
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_CLIENT_CODE (long nOrderDescriptor); 
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_ORDER_FIRMID (long nOrderDescriptor); 

long TRANS2QUIK_API __stdcall TRANS2QUIK_SUBSCRIBE_TRADES (LPSTR ClassCode, LPSTR Seccodes);
long TRANS2QUIK_API __stdcall TRANS2QUIK_UNSUBSCRIBE_TRADES ();
long TRANS2QUIK_API __stdcall TRANS2QUIK_START_TRADES(TRANS2QUIK_TRADE_STATUS_CALLBACK pfnTradeStatusCallback);

long TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_DATE (long nTradeDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_SETTLE_DATE (long nTradeDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_TIME (long nTradeDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_IS_MARGINAL (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_ACCRUED_INT (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_YIELD (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_TS_COMMISSION (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_CLEARING_CENTER_COMMISSION (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_EXCHANGE_COMMISSION (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_TRADING_SYSTEM_COMMISSION (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_PRICE2 (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_REPO_RATE (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_REPO_VALUE (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_REPO2_VALUE (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_ACCRUED_INT2 (long nTradeDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_REPO_TERM (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_START_DISCOUNT (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_LOWER_DISCOUNT (long nTradeDescriptor);
double TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_UPPER_DISCOUNT (long nTradeDescriptor);
long TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_BLOCK_SECURITIES (long nTradeDescriptor);

LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_CURRENCY (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_SETTLE_CURRENCY (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_SETTLE_CODE (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_ACCOUNT (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_BROKERREF (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_CLIENT_CODE (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_USERID (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_FIRMID (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_PARTNER_FIRMID (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_EXCHANGE_CODE (long nTradeDescriptor);
LPTSTR TRANS2QUIK_API __stdcall TRANS2QUIK_TRADE_STATION_ID (long nTradeDescriptor);

#ifdef __cplusplus
}
#endif
