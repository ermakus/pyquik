#pragma once
#include <windows.h>
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

	std::string getString(int r, int c);
	double		getDouble(int r, int c);
	void		setString(int r, int c, std::string val);
	void		setDouble(int r, int c, double val);
};

class MarketListener {
public:
	MarketListener() {}
	virtual ~MarketListener() {}
	virtual void onTableData( const char* topic, const char* item, Table* table ) {};
	virtual void onConnected() {};
	virtual void onDisconnected() {};
	virtual void onTransactionResult(long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, unsigned long dwTransId, double dOrderNum, std::string message) {}
};

class Market {

  CMarketServer* m_pDataSource;
  DWORD		 m_dwThreadId;
  long		 m_nExtendedErrorCode;
  long		 m_nResult;

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

  virtual void setDebug(bool enabled);

  virtual std::string errorMessage();
  virtual long        errorCode() { return m_nExtendedErrorCode; }


};




  
