#ifndef _STDDDE_
#define _STDDDE_

#include <ddeml.h>
#include <list>
//#include "types.h"

//
// String names for standard Windows Clipboard formats
//

#define SZCF_TEXT           "TEXT"        
#define SZCF_BITMAP         "BITMAP"      
#define SZCF_METAFILEPICT   "METAFILEPICT"
#define SZCF_SYLK           "SYLK"        
#define SZCF_DIF            "DIF"         
#define SZCF_TIFF           "TIFF"        
#define SZCF_OEMTEXT        "OEMTEXT"     
#define SZCF_DIB            "DIB"         
#define SZCF_PALETTE        "PALETTE"     
#define SZCF_PENDATA        "PENDATA"     
#define SZCF_RIFF           "RIFF"     
#define SZCF_WAVE           "WAVE"     
#define SZCF_UNICODETEXT    "UNICODETEXT" 
#define SZCF_ENHMETAFILE    "ENHMETAFILE" 

//
// String names for some standard DDE strings not
// defined in DDEML.H
//

#define SZ_READY            "Ready"
#define SZ_BUSY             "Busy"
#define SZ_TAB              "\t"
#define SZ_RESULT           "Result"
#define SZ_PROTOCOLS        "Protocols"
#define SZ_EXECUTECONTROL1  "Execute Control 1"


#ifdef _UNICODE
#define DDE_CODEPAGE CP_WINUNICODE
#else
#define DDE_CODEPAGE CP_WINANSI
#endif

//
// Helpers
//
static String GetFormatName(WORD wFmt);

//
// Generic counted object class
//

class CDDECountedObject
{
public:
    CDDECountedObject();
    virtual ~CDDECountedObject();
    int AddRef();
    int Release();

private:
    int m_iRefCount;
};
    
//
// String handle class
//

class CDDEServer;

class CHSZ
{
public:
    CHSZ();
    CHSZ(CDDEServer* pServer, LPCTSTR szName);
    virtual ~CHSZ();
    void Create(CDDEServer* pServer, LPCTSTR szName);
    operator HSZ() {return m_hsz;}

    HSZ m_hsz;

protected:
    DWORD m_dwDDEInstance;
};

//
// DDE item class
//

class CDDETopic;

class CDDEItem
{
public:
    CDDEItem();
    virtual ~CDDEItem();
    void Create(LPCTSTR pszName);
    void PostAdvise();
    virtual BOOL Request(UINT wFmt, void** ppData, DWORD* pdwSize);
    virtual BOOL Poke(UINT wFmt, void* pData, DWORD dwSize);
    virtual BOOL IsSupportedFormat(WORD wFormat);
    virtual WORD* GetFormatList()
        {return NULL;}
    virtual BOOL CanAdvise(UINT wFmt);

    String m_strName;          // name of this item
    CDDETopic* m_pTopic;        // pointer to the topic it belongs to

protected:
};

//
// String item class
//

class CDDEStringItem : public CDDEItem
{
public:
    virtual void OnPoke(){;}
    virtual void SetData(const char * pszData);
    virtual LPCTSTR GetData()
        {return (LPCTSTR)m_strData;}
    operator LPCTSTR()
        {return (LPCTSTR)m_strData;}

protected:
    virtual BOOL Request(UINT wFmt, void** ppData, DWORD* pdwSize);
    virtual BOOL Poke(UINT wFmt, void* pData, DWORD dwSize);
    virtual WORD* GetFormatList();

    String m_strData;
};

//
// Item list class
//

class CDDEItemList : public std::list<CDDEItem*>
{
public:
    CDDEItemList();
    virtual ~CDDEItemList();
#if 0
    CDDEItem* GetNext(POSITION& rPosition) const
        {return (CDDEItem*)CObList::GetNext(rPosition);}
#else
	void AddTail(CDDEItem * pItem);
#endif
};

//
// Topic class
//

class CDDEServer;

class CDDETopic
{
public:
    CDDETopic();
    virtual ~CDDETopic();
    void Create(LPCTSTR pszName);
    BOOL AddItem(CDDEItem* pItem);
    virtual BOOL Request(UINT wFmt, LPCTSTR pszItem,
                         void** ppData, DWORD* pdwSize);
    virtual BOOL Poke(UINT wFmt, LPCTSTR pszItem, void* pData, DWORD dwSize);
    virtual BOOL Exec(void* pData, DWORD dwSize);
    virtual CDDEItem* FindItem(LPCTSTR pszItem);
    virtual BOOL CanAdvise(UINT wFmt, LPCTSTR pszItem);
    void PostAdvise(CDDEItem* pItem);

    String m_strName;          // name of this topic
    CDDEServer* m_pServer;      // ptr to the server which owns this topic
    CDDEItemList m_ItemList;    // List of items for this topic

protected:
};

//
// Topic list class
//

class CDDETopicList : public std::list<CDDETopic*>
{
public:
    CDDETopicList();
    virtual ~CDDETopicList();
#if 0
    CDDETopic* GetNext(POSITION& rPosition) const
        {return (CDDETopic*)CObList::GetNext(rPosition);}
#else
	int GetCount () const { return size(); };
	void AddTail(CDDETopic * pItem);
#endif
protected:

};

//
// Conversation class
//

class CDDEConv : public CDDECountedObject
{
public:
    CDDEConv();
    CDDEConv(CDDEServer* pServer);
    CDDEConv(CDDEServer* pServer, HCONV hConv, HSZ hszTopic);
    virtual ~CDDEConv();
    virtual BOOL ConnectTo(LPCTSTR pszService, LPCTSTR pszTopic);
    virtual BOOL Terminate();
    virtual BOOL AdviseData(UINT wFmt, LPCTSTR pszTopic, LPCTSTR pszItem,
                            void* pData, DWORD dwSize);
    virtual BOOL Request(LPCTSTR pszItem, void** ppData, DWORD* pdwSize);
    virtual BOOL Advise(LPCTSTR pszItem);
    virtual BOOL Exec(LPCTSTR pszCmd);
    virtual BOOL Poke(UINT wFmt, LPCTSTR pszItem, void* pData, DWORD dwSize);

    CDDEServer* m_pServer;
    HCONV   m_hConv;            // Conversation handle
    HSZ     m_hszTopic;         // Topic name

};

//
// Conversation list class
//

class CDDEConvList : public std::list<CDDEConv*>
{
public:
    CDDEConvList();
    virtual ~CDDEConvList();
#if 0
    CDDEConv* GetNext(POSITION& rPosition) const
        {return (CDDEConv*)CObList::GetNext(rPosition);}
#else
	void AddTail(CDDEConv * pItem);
	typedef std::list<CDDEConv*>::iterator POSITION;
	void RemoveAt(POSITION pos) { this->erase(pos); }
#endif
    
protected:

};

//
// Topics and items used to support the 'system' topic in the server
//

class CDDESystemItem : public CDDEItem
{
protected:
    virtual WORD* GetFormatList();
};

class CDDESystemItem_TopicList : public CDDESystemItem
{
protected:
    virtual BOOL Request(UINT wFmt, void** ppData, DWORD* pdwSize);
};

class CDDESystemItem_ItemList : public CDDESystemItem
{
protected:
    virtual BOOL Request(UINT wFmt, void** ppData, DWORD* pdwSize);
};

class CDDESystemItem_FormatList : public CDDESystemItem
{
protected:
    virtual BOOL Request(UINT wFmt, void** ppData, DWORD* pdwSize);
};

class CDDEServerSystemTopic : public CDDETopic
{
protected:
    virtual BOOL Request(UINT wFmt, LPCTSTR pszItem,
                         void** ppData, DWORD* pdwSize);

};


//
// Server class
// Note: this class is for a server which supports only one service
//

class CDDEServer
{
public:
    CDDEServer();
    virtual ~CDDEServer();
    BOOL Create(LPCTSTR pszServiceName,
                DWORD dwFilterFlags = 0,
                DWORD* pdwDDEInst = NULL);
    virtual void Shutdown(int flags = 0);
	virtual void Uninitialize();
    virtual BOOL OnCreate() {return TRUE;}
    virtual UINT GetLastError()
        {return ::DdeGetLastError(m_dwDDEInstance);}
    virtual HDDEDATA CustomCallback(WORD wType,
                                    WORD wFmt,
                                    HCONV hConv,
                                    HSZ hsz1,
                                    HSZ hsz2,
                                    HDDEDATA hData,
                                    DWORD dwData1,
                                    DWORD dwData2)
        {return NULL;}

    virtual BOOL Request(UINT wFmt, LPCTSTR pszTopic, LPCTSTR pszItem,
                         void** ppData, DWORD* pdwSize);
    virtual BOOL Poke(UINT wFmt, LPCTSTR pszTopic, LPCTSTR pszItem,
                      void* pData, DWORD dwSize);
    virtual BOOL AdviseData(UINT wFmt, HCONV hConv, LPCTSTR pszTopic, LPCTSTR pszItem,
                      void* pData, DWORD dwSize);
    virtual BOOL Exec(LPCTSTR pszTopic, void* pData, DWORD dwSize);
    virtual void Status(const char * pszFormat, ...) {;}
    virtual BOOL AddTopic(CDDETopic* pTopic);
    String StringFromHsz(HSZ hsz);
    virtual BOOL CanAdvise(UINT wFmt, LPCTSTR pszTopic, LPCTSTR pszItem);
    void PostAdvise(CDDETopic* pTopic, CDDEItem* pItem);
    CDDEConv*  AddConversation(HCONV hConv, HSZ hszTopic);
    CDDEConv* AddConversation(CDDEConv* pNewConv);
    BOOL RemoveConversation(HCONV hConv);
    CDDEConv*  FindConversation(HCONV hConv);

    DWORD       m_dwDDEInstance;        // DDE Instance handle
    CDDETopicList m_TopicList;          // topic list

protected:
    BOOL        m_bInitialized;         // TRUE after DDE init complete
    String     m_strServiceName;       // Service name
    CHSZ        m_hszServiceName;       // String handle for service name
    CDDEConvList m_ConvList;            // Conversation list
	String m_clientName;

    HDDEDATA DoWildConnect(HSZ hszTopic);
    BOOL DoCallback(WORD wType,
                WORD wFmt,
                HCONV hConv,
                HSZ hsz1,
                HSZ hsz2,
                HDDEDATA hData,
                HDDEDATA *phReturnData);
    CDDETopic* FindTopic(LPCTSTR pszTopic);

	virtual int OnXTypConnect(LPCTSTR name) { return 0; }
	virtual int OnXTypDisconnect(HCONV hConv) { return 0; }

	void SetClientName(const String & name) { m_clientName = name; }
	LPCTSTR GetClientName() const { return m_clientName; }

private:
    static HDDEDATA CALLBACK StdDDECallback(WORD wType,
                                            WORD wFmt,
                                            HCONV hConv,
                                            HSZ hsz1,
                                            HSZ hsz2,
                                            HDDEDATA hData,
                                            DWORD dwData1,
                                            DWORD dwData2);

    CDDEServerSystemTopic m_SystemTopic;
    CDDESystemItem_TopicList m_SystemItemTopics;
    CDDESystemItem_ItemList m_SystemItemSysItems;
    CDDESystemItem_ItemList m_SystemItemItems;
    CDDESystemItem_FormatList m_SystemItemFormats;
};          


#endif // _STDDDE_
