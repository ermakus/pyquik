#ifndef _MYSERV_
#define _MYSERV_

#define DDE_SERVER_NAME TEXT("QuikDDE")

#include <list>

#include "market.h"
#include "table.h"
#include "dde.h"

class CMarketServer : public CDDEServer
{
public:
    CMarketServer();
    virtual ~CMarketServer();

	virtual void Shutdown(int flags = 0);
    virtual BOOL OnCreate();
	virtual BOOL Poke(UINT wFmt, LPCTSTR pszTopic, LPCTSTR pszItem, void* pData, DWORD dwSize);
	BOOL PokeCache(LPCTSTR pszTopic, void* pData, DWORD dwSize);

	typedef std::list<MarketListener*> MarketListeners;

	virtual void OnConnected();
	virtual void OnDisconnected();
	virtual void OnTransactionResult(long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, unsigned long dwTransId, double dOrderNum, const char* lpcstrTransactionReplyMessage);

	MarketListeners m_listeners;
protected:
	BOOL ParseData(Table& table, PBYTE data, DWORD length);
};


#endif // _MYSERV_
