#include "quikdde.h"
#include "trans2quik_api.h"

static DWORD	      s_dwThreadId = 0;
static Market*        s_pMarket = NULL;
static char			  s_szErrorMessage [1024];

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

static void setErrorMessage(const char* msg)
{
    strncpy( s_szErrorMessage, cp1251_to_utf8( msg ).c_str(), sizeof(s_szErrorMessage) );
}

BOOL WINAPI ConsoleHandler(DWORD CEvent)
{
    switch(CEvent)
    {
		case CTRL_C_EVENT:
		case CTRL_BREAK_EVENT:
		case CTRL_CLOSE_EVENT:
		case CTRL_LOGOFF_EVENT:
		case CTRL_SHUTDOWN_EVENT:
			::PostThreadMessage( s_dwThreadId, WM_QUIT, 0, 0 );
        break;
    }
    return TRUE;
}

enum ddt {tdtFloat=1, tdtString, tdtBool, tdtError, tdtBlank, tdtInt, tdtSkip, tdtTable = 16}; 

HDDEDATA CALLBACK DDE_Callback(UINT uType, UINT uFmt, HCONV hConv, HSZ hsz1, HSZ hsz2, HDDEDATA hData, DWORD dwData1, DWORD dwData2)
{
	switch (uType)
	{
        case XTYP_CONNECT:
        {
            return (HDDEDATA)TRUE;
        }

	    case XTYP_POKE:	
		{
			CHAR topic[200], item[200];
		    DdeQueryStringA(s_pMarket->m_dwInst,hsz1,topic,200,CP_WINANSI);
		    DdeQueryStringA(s_pMarket->m_dwInst,hsz2,item,200,CP_WINANSI);
            DWORD length = DdeGetData(hData, NULL, 0, 0);
            if (length > 8)
            {
                BYTE* data = new BYTE[length]; 
                DdeGetData(hData,data,length,0);
	            Table table;
	            s_pMarket->ParseData( table, data, length );
		        s_pMarket->onTableData( (char*)cp1251_to_utf8(topic).c_str(), (char*)cp1251_to_utf8(item).c_str(), &table );
                delete[] data;
            }
	        return((HDDEDATA)DDE_FACK); 
	    }

	    case XTYP_DISCONNECT:
	    {
			break;
	    }

	    case XTYP_ERROR:
	    {
            break;
        }
    }
    return((HDDEDATA)NULL);
}


extern "C" 
void __stdcall TRANS2QUIK_ConnectionStatusCallback (long nConnectionEvent, long nExtendedErrorCode, LPCSTR lpcstrInfoMessage)
{
	if( s_pMarket ) 
	{
			if(lpcstrInfoMessage) setErrorMessage( lpcstrInfoMessage );
			if (nConnectionEvent == TRANS2QUIK_DLL_CONNECTED) 
				s_pMarket->onConnected();
			if (nConnectionEvent == TRANS2QUIK_DLL_DISCONNECTED) 
				s_pMarket->onDisconnected();
			if (nConnectionEvent == TRANS2QUIK_QUIK_CONNECTED) 
				s_pMarket->onConnected();
			if (nConnectionEvent == TRANS2QUIK_QUIK_DISCONNECTED) 
				s_pMarket->onDisconnected();
	}
}

extern "C" 
void __stdcall TRANS2QUIK_TransactionsReplyCallback (long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, 
                                                                DWORD dwTransId, double dOrderNum, LPCSTR lpcstrTransactionReplyMessage)
{
	if( s_pMarket ) {
        if(lpcstrTransactionReplyMessage) setErrorMessage( lpcstrTransactionReplyMessage );
		s_pMarket->onTransactionResult(nTransactionResult,nTransactionExtendedErrorCode, nTransactionReplyCode, dwTransId, dOrderNum);
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Market class

Market::Market(MarketCallback cb) : m_dwInst( 0 ), m_Callback( cb )
{
    s_pMarket = this;
    setErrorMessage("OK");
}

Market::~Market() {
}

const char* Market::errorMessage() 
{
    return s_szErrorMessage;
}

long Market::connect(const char* quickDir) {
    long ex;
	long result = TRANS2QUIK_SET_CONNECTION_STATUS_CALLBACK (TRANS2QUIK_ConnectionStatusCallback, &ex, s_szErrorMessage, sizeof (s_szErrorMessage));

	if (result != TRANS2QUIK_SUCCESS) {
        setErrorMessage( s_szErrorMessage );
        return result;
    }
	
	result = TRANS2QUIK_SET_TRANSACTIONS_REPLY_CALLBACK (TRANS2QUIK_TransactionsReplyCallback, &ex, s_szErrorMessage, sizeof (s_szErrorMessage));
	if (result != TRANS2QUIK_SUCCESS) {
        setErrorMessage( s_szErrorMessage );
        return result;
    }

	result = TRANS2QUIK_CONNECT ((char*)quickDir, &ex, s_szErrorMessage, sizeof (s_szErrorMessage));
	if (result != TRANS2QUIK_SUCCESS) {
        setErrorMessage( s_szErrorMessage );
        return result;
    }
    setErrorMessage("OK");
	return result;
}

long Market::disconnect() {
    long ex;
	long result = TRANS2QUIK_DISCONNECT(&ex, s_szErrorMessage, sizeof (s_szErrorMessage));
	if (result != TRANS2QUIK_SUCCESS) {
        setErrorMessage( s_szErrorMessage );
        return result;
    }
    setErrorMessage("OK");
	return result;
}

long Market::sendAsync(const char* trans) {
    long ex;
	long result = TRANS2QUIK_SEND_ASYNC_TRANSACTION ((char*)trans, &ex, s_szErrorMessage, sizeof (s_szErrorMessage));
   	if (result != TRANS2QUIK_SUCCESS) {
        setErrorMessage( s_szErrorMessage );
        return result;
    }
    setErrorMessage("OK");
	return result;
}

void Market::run() 
{
	s_dwThreadId = m_dwThreadId = ::GetCurrentThreadId();
	SetConsoleCtrlHandler( (PHANDLER_ROUTINE)ConsoleHandler,TRUE);

	MSG msg;
	int err;
	
	while( (err = GetMessage(&msg,NULL,0,0)) != 0 )
	{
		if( err == -1 ) 
			break;
		TranslateMessage(&msg);
		DispatchMessage(&msg);
	}
}

void Market::stop() {
	::PostThreadMessage( m_dwThreadId, WM_QUIT, 0, 0 );
}


long Market::ddeConnect(const char* serverName)
{
	if(!RegisterClipboardFormatA((LPSTR)"XlTable"))
    {
        setErrorMessage("Can't register XlTable format");
        return 1;
    }
	if(DdeInitialize(&m_dwInst, DDE_Callback, APPCLASS_STANDARD, 0))
    {
        setErrorMessage("Can't init DDE");
        return 1;
    }
	m_hszService = DdeCreateStringHandleA(m_dwInst, serverName, CP_WINANSI);
	if(m_hszService == 0)
    {
        setErrorMessage("Can't create DDE handle");
        return 1;
    }
	if(!DdeNameService(m_dwInst, m_hszService, NULL, DNS_REGISTER))
    {
        setErrorMessage("Can't create DDE service");
        return 1;
    }
	return 0;
}

void Market::ddeDisconnect()
{
	if (m_dwInst)
	{
		DdeNameService(m_dwInst, m_hszService, (HSZ)NULL, DNS_UNREGISTER);
		if(m_hszService) DdeFreeStringHandle(m_dwInst, m_hszService);
		DdeUninitialize(m_dwInst);
		m_dwInst = 0;
	}
}
  
void Market::onTableData( char* topic, char* item, Table* table )
{
    MarketEvent event;
    event.type = ET_DATA;
    event.item  = item;
    event.topic = topic;
    event.table = table;
    m_Callback( &event );
}

void Market::onConnected()
{
    MarketEvent event;
    event.type = ET_CONNECT;
    m_Callback( &event );
}

void Market::onDisconnected()
{
    MarketEvent event;
    event.type = ET_DISCONNECT;
    m_Callback( &event );
}


void Market::onTransactionResult(long nTransactionResult, long nTransactionExtendedErrorCode, long nTransactionReplyCode, 
                                        unsigned long dwTransId, double dOrderNum )
{
    MarketEvent event;
    event.type = ET_TRANS;
    m_Callback( &event );
}

BOOL Market::ParseData(Table& table, PBYTE data, DWORD length)
{
	 WORD row_n	= 0;
	 WORD col_n = 0;
     UINT offset  = 0; 
	 WORD cnum = 0, rnum = 0;
	 WORD cb = 0;
	 WORD size = 0;
	 WORD type = 0;
	 string str;
          
     union
     {
           WORD w; 
           double d; 
           BYTE b[8];
     } conv;  

     if (length < 8) return 1;               


     conv.b[0] = data[offset++];
     conv.b[1] = data[offset++];
	 if (conv.w != tdtTable) return 1;
   
     conv.b[0] = data[offset++];
     conv.b[1] = data[offset++];
	 if (conv.w != 4) return 1;

     conv.b[0] = data[offset++];
     conv.b[1] = data[offset++];
     row_n = conv.w;

     conv.b[0] = data[offset++];
     conv.b[1] = data[offset++];
     col_n = conv.w;

	 if (!col_n || !row_n)
     {
         return 1;
     }    

	 table.init(row_n, col_n);
  
	 while (offset < length)
	 {
		 conv.b[0] = data[offset++];
	     conv.b[1] = data[offset++];
		 type = conv.w;

		 switch(type)
		 {
		 case tdtFloat:
			 {
	 			conv.b[0] = data[offset++];
				conv.b[1] = data[offset++];
				cb = conv.w;
				if (cb%8) 
				{
					return 1;
				}
				for (int tmp=0, i=0; i < cb; i++, tmp++)
				{
					conv.b[tmp] = data[offset++];
					if (tmp == 7)
					{
						 tmp = -1;
						 /*
						 str = DoubleToString(conv.d);
						 if (!str.compare("")) 
						 {
							 return 1;
						 }
						 */
						 table.setString(rnum,cnum,"DOUBLE");
						 table.setDouble(rnum,cnum,conv.d);
						 cnum++;
						 if (cnum == table.cols())
						 {
							 cnum = 0;
							 rnum++;
						 }
					 }
				}
			 }
			 break;

		 case tdtString:
			 {
			     conv.b[0] = data[offset++];
			     conv.b[1] = data[offset++];
			     cb = conv.w;

        		 for (WORD i = 0; i < cb; )
			     {
				    size = data[offset++];
					
					string s;
				    for(int j = 0; j < size; j++)
                        s.push_back(data[offset++]);
					table.setString(rnum,cnum, s.c_str() );
				    i += 1 + size;
				    cnum++;
				    if (cnum == table.cols())
				    {
					   cnum = 0;
					   rnum++;
			        }
                 }
			 }
			 break;

		 case tdtBool:
			 {
			     conv.b[0] = data[offset++];
			     conv.b[1] = data[offset++];
			     cb = conv.w;
			     if (cb%2) 
			     {
					 table.reset();
 				     return 1;
		         }
			     for (int tmp=0, i=0; i < cb; i++, tmp++)
			     {
				     conv.b[tmp] = data[offset++];
				     if (tmp == 1)
				     {
					    tmp = -1;
						table.setString(rnum,cnum,"BOOL");
						if (conv.w) table.setDouble(rnum,cnum,1);
					    else table.setDouble(rnum,cnum,0);
					    cnum++;
					    if (cnum == table.cols())
					    {
						   cnum = 0;
						   rnum++;
                        }
                     }
                 }
			 }
			 break;

		 case tdtError:
			 {
                 conv.b[0] = data[offset++];
			     conv.b[1] = data[offset++];
			     cb = conv.w;
			     if (cb%2) 
			     {
				     table.reset();
				     return 1;
                 }
			     for (int tmp=0, i=0; i < cb; i++, tmp++)
			     {
				     conv.b[tmp] = data[offset++];
				     if (tmp == 1)
				     {
					    tmp = -1;
					    table.setString(rnum,cnum,"ERROR");
					    cnum++;
					    if (cnum == table.cols())
					    {
						    cnum = 0;
						    rnum++;
				        }
				     }
		         }
			 }
			 break;

		 case tdtBlank:
			 {
                 conv.b[0] = data[offset++];
			     conv.b[1] = data[offset++];
			     cb = conv.w;
			     if (cb != 2)
			     {
				     table.reset();
				     return 1;
		         }
			     conv.b[0] = data[offset++];
			     conv.b[1] = data[offset++];
			     size = conv.w;
			     for (int i = 0; i<size; i++)
			     {
				     table.setString(rnum,cnum, "NULL");
				     cnum++;
				     if (cnum == table.cols())
				     {
					     cnum = 0;
					     rnum++;
			         }
	             }
			 }
			 break;

		 case tdtInt:
			 {
                 conv.b[0] = data[offset++];
			     conv.b[1] = data[offset++];
			     cb = conv.w;
			     if (cb%2) 
			     {
				     table.reset();
				     return 1;
		         }
			     for (int tmp=0, i=0; i < cb; i++, tmp++)
			     {
				     conv.b[tmp] = data[offset++];
				     if (tmp == 1)
				     {
					     tmp = -1;
						 //_itoa_s(conv.w,mas,10);
						 table.setString(rnum,cnum,"INT");
						 table.setDouble(rnum,cnum,conv.w);
					     cnum++;
					     if (cnum == table.cols())
					     {
						     cnum = 0;
						     rnum++;
				         }
		             }
			     }
			 }
			 break;

		 case tdtSkip:
		     {
				 table.reset();
				 return 1;
             }
		 }
	 }

	 return 0;
}


//////////////////////////////////////////////////////////////////////////////////
// Table

Table::Table() {
}

Table::~Table() {
}

void Table::init(int r, int c) {
	stable.init( r, c, "" );
	dtable.init( r, c, 0.0 );
}

void Table::reset() {
	stable.reset();
	dtable.reset();
}

int Table::cols() { 
	return stable.cols; 
}

int Table::rows() { 
	return stable.rows; 
}

char* Table::getString(int r, int c) {
	return (char*)stable[r][c].c_str();
}

double Table::getDouble(int r, int c) {
	return dtable[r][c];
}

void Table::setString(int r, int c, std::string val) {
	stable[r][c] = cp1251_to_utf8(val.c_str());
}

void Table::setDouble(int r, int c, double val) {
	dtable[r][c] = val;
}


