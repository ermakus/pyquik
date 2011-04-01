#ifndef _MYSERV_
#define _MYSERV_

#include <windows.h>

#include <list>
#include <string>
#include <ddeml.h>

#include "market.h"
#include "table.h"

class CMarketServer 
{
    friend HDDEDATA CALLBACK DDE_Callback(UINT uType, UINT uFmt, HCONV hConv, HSZ hsz1, HSZ hsz2, HDDEDATA hData, DWORD dwData1, DWORD dwData2);
public:
    CMarketServer(std::string name);
    virtual ~CMarketServer();

	typedef std::list<MarketListener*> MarketListeners;

	virtual bool Connect();
	virtual void Disconnect();

	virtual void OnConnected();
	virtual void OnDisconnected();
	virtual void OnTransactionResult(long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, unsigned long dwTransId, 
                                     double dOrderNum, const char* lpcstrTransactionReplyMessage);

	std::string m_strName;
	DWORD       m_dwInst;
	HSZ         m_hszService;

	MarketListeners m_listeners;
	BOOL ParseData(Table& table, PBYTE data, DWORD length);
};


static std::string cp1251_to_utf8(const char *str)
{
	std::string res;	
	int result_u, result_c;
	result_u = MultiByteToWideChar(1251,0,str,-1,0,0);
	if (!result_u) return 0;
	wchar_t *ures = new wchar_t[result_u];
	if(!MultiByteToWideChar(1251,0,str,-1,ures,result_u))
	{
		delete[] ures;
		return 0;
	}
	result_c = WideCharToMultiByte(CP_UTF8,0,ures,-1,0,0,0, 0);
	if(!result_c)
	{
		delete [] ures;
		return 0;
	}
	char *cres = new char[result_c];
	if(!WideCharToMultiByte(CP_UTF8,0,ures,-1,cres,result_c,0, 0))
	{
		delete[] cres;
		return 0;
	}
	delete[] ures;
	res.append(cres);
	delete[] cres;
	return res;
}

#endif
