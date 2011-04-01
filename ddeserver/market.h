#ifndef MARKET_H
#define MARKET_H

#include <windows.h>

#include <list>
#include <string>
#include <ddeml.h>

#include "table.h"

class Table {

	TableDataString stable;
	TableDataDouble dtable;

public:
	Table();
	virtual ~Table();

	void init(int r, int c);
	void reset();

	int cols();
	int rows();

	std::string getString(int r, int c);
	double		getDouble(int r, int c);
	void		setString(int r, int c, std::string val);
	void		setDouble(int r, int c, double val);
};

typedef enum {
    ET_CONNECT,
    ET_DISCONNECT,
    ET_DATA,
    ET_TRANS
} MarketEventType;

struct MarketEvent
{
    MarketEventType  type;
    const char*   topic;
    const char*   item;
    Table*  table;
    long    result;
    long    errorCode;
    long    reply;
    unsigned long tid;
    double order;
};

typedef void (*MarketCallback)(MarketEvent* evt);

class Market 
{
  friend HDDEDATA CALLBACK DDE_Callback(UINT uType, UINT uFmt, HCONV hConv, HSZ hsz1, HSZ hsz2, HDDEDATA hData, DWORD dwData1, DWORD dwData2);
public:
  Market(MarketCallback callback);
  virtual ~Market();

  virtual long connect(const char* quickDir);
  virtual long disconnect();
  virtual long sendAsync(const char* trans);

  virtual long ddeConnect(const char* serverName);
  virtual void ddeDisconnect();
  virtual void run();
  virtual void stop();

  virtual const char* errorMessage();

  virtual void onConnected();
  virtual void onDisconnected();
  virtual void onTransactionResult(long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, unsigned long dwTransId, double dOrderNum);
  virtual void onTableData( const char* topic, const char* item, Table* table );

private:
  DWORD		  m_dwThreadId;
  long		  m_nResult;
  DWORD       m_dwInst;
  HSZ         m_hszService;
   
  MarketCallback m_Callback;
  BOOL ParseData(Table& table, PBYTE data, DWORD length);
};


#endif
