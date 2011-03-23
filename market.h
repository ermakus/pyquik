#pragma once
#include <Windows.h>
#include "table.h"

class CMarketServer;

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

	const char* getString(int r, int c);
	double		getDouble(int r, int c);
	void		setString(int r, int c, const char* val);
	void		setDouble(int r, int c, double val);
};

class MarketListener {
public:
	MarketListener() {}
	virtual ~MarketListener() {}
	virtual void onTableData( const char* topic, const char* item, Table* table ) {};
	virtual void onConnected() {};
	virtual void onDisconnected() {};
	virtual void onTransactionResult(long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, unsigned long dwTransId, double dOrderNum, const char* lpcstrTransactionReplyMessage) {}
};

class Market {

  CMarketServer* m_pDataSource;
  DWORD		 m_dwThreadId;
  long		 m_nExtendedErrorCode;
  long		 m_nResult;
  char		 m_szErrorMessage [1024];

public:
  Market();
  virtual ~Market();

  virtual void addListener( MarketListener* pListener );
  virtual void removeListener( MarketListener* pListener );

  virtual void run();
  virtual void stop();

  virtual long connect(const char* quickDir);
  virtual long disconnect();

  virtual long sendAsync(const char* trans);

  virtual const char* errorMessage() { return m_szErrorMessage; }
  virtual long        errorCode() { return m_nExtendedErrorCode; }


};




  
