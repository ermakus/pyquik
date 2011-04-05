#ifndef MARKET_H
#define MARKET_H

#include <windows.h>
#include <ddeml.h>

#include <list>
#include <string>
#include <vector>
#include <deque>

using std::string;
using std::vector;

template<typename T> 
class TableData : public vector< vector< T > > {

public:
	DWORD rows;
	DWORD cols;
	
	TableData() : rows(0), cols(0) {
	}

	void init(DWORD r, DWORD c, const T& s) {
		assign(r, std::vector< T >(c,s));
		rows = r;
		cols = c;
	}

	void reset() {
		this->clear();
		rows = cols = 0;
	}
};

typedef TableData<string> TableDataString;
typedef TableData<double> TableDataDouble;

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

	char* getString(int r, int c);
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
    char*   topic;
    char*   item;
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
  virtual void onTableData( char* topic, char* item, Table* table );

private:
  DWORD		  m_dwThreadId;
  long		  m_nResult;
  DWORD       m_dwInst;
  HSZ         m_hszService;
  std::deque<MarketEvent> m_EventQueue;
  MarketCallback m_Callback;
  BOOL ParseData(Table& table, PBYTE data, DWORD length);
};


#endif
