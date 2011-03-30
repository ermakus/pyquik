
cdef extern from "numpy/arrayobject.h":
    ctypedef int intp
    ctypedef extern class numpy.ndarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef intp *dimensions
        cdef intp *strides
        cdef int flags

cdef extern from "ta_common.h":
    ctypedef int TA_RetCode
    struct TA_StringTable:
        int size
        char** string

cdef extern from "ta_abstract.h":

    ctypedef unsigned int TA_FuncHandle
    ctypedef unsigned int TA_FuncFlags
    ctypedef int TA_InputFlags
    ctypedef int TA_OptInputFlags
    ctypedef int TA_OutputFlags

    ctypedef int TA_InputParameterType  
    enum: TA_Input_Price
    enum: TA_Input_Real
    enum: TA_Input_Integer

    ctypedef int TA_OptInputParameterType  
    enum: TA_OptInput_RealRange
    enum: TA_OptInput_RealList
    enum: TA_OptInput_IntegerRange
    enum: TA_OptInput_IntegerList

    ctypedef int TA_OutputParameterType  
    enum: TA_Output_Real
    enum: TA_Output_Integer


    enum: TA_FUNC_FLG_OVERLAP
    enum: TA_FUNC_FLG_VOLUME
    enum: TA_FUNC_FLG_UNST_PER
    enum: TA_FUNC_FLG_CANDLESTICK


    struct TA_FuncInfo:
        char * name
        char * group
        char * hint
        char * camelCaseName
        TA_FuncFlags flags
        unsigned int nbInput
        unsigned int nbOptInput
        unsigned int nbOutput
        TA_FuncHandle *handle

    struct TA_RealRange:
        double min
        double max
        int precision
        double suggested_start
        double suggested_end
        double suggested_increment

    struct TA_IntegerRange:
        int min
        int max
        int precision
        int suggested_start
        int suggested_end
        int suggested_increment

    struct TA_RealDataPair:
        double  value
        char *string

    struct TA_IntegerDataPair:
        int  value
        char *string

    struct TA_RealList:
        TA_RealDataPair *data
        unsigned int nbElement

    struct TA_IntegerList:
        TA_IntegerDataPair *data
        unsigned int nbElement


    struct TA_InputParameterInfo:
        TA_InputParameterType type
        char *paramName
        TA_InputFlags flags

    struct TA_OptInputParameterInfo:
        TA_OptInputParameterType type
        char *paramName
        TA_OptInputFlags flags
        char *displayName
        void *dataSet
        double defaultValue
        char *hint
        char *helpFile

    struct TA_OutputParameterInfo:
        TA_OutputParameterType type
        char  *paramName
        TA_OutputFlags flags

    struct TA_ParamHolder:
        pass

    TA_RetCode TA_GroupTableAlloc( TA_StringTable **table )
    TA_RetCode TA_GroupTableFree( TA_StringTable *table )
    TA_RetCode TA_FuncTableAlloc( char *group, TA_StringTable **table )                              
    TA_RetCode TA_FuncTableFree( TA_StringTable *table )
    TA_RetCode TA_GetFuncHandle( char *name, TA_FuncHandle **handle )
    TA_RetCode TA_GetFuncInfo( TA_FuncHandle *handle, TA_FuncInfo **funcInfo )
    TA_RetCode TA_ParamHolderAlloc( TA_FuncHandle *handle, TA_ParamHolder **allocatedParams )
    TA_RetCode TA_ParamHolderFree( TA_ParamHolder *params )
    TA_RetCode TA_GetInputParameterInfo( TA_FuncHandle *handle, unsigned int paramIndex, TA_InputParameterInfo **info )
    TA_RetCode TA_GetOptInputParameterInfo( TA_FuncHandle *handle, unsigned int paramIndex, TA_OptInputParameterInfo **info )
    TA_RetCode TA_GetOutputParameterInfo( TA_FuncHandle *handle, unsigned int paramIndex, TA_OutputParameterInfo **info )
    TA_RetCode TA_SetInputParamIntegerPtr( TA_ParamHolder *params, unsigned int paramIndex, int *value )
    TA_RetCode TA_SetInputParamRealPtr( TA_ParamHolder *params,  unsigned int paramIndex, double *value )
    TA_RetCode TA_SetInputParamPricePtr( TA_ParamHolder *params, unsigned int paramIndex, double *open, double *high, double *low, double *close,double *volume,double *openInterest )
    TA_RetCode TA_SetOptInputParamInteger( TA_ParamHolder *params, unsigned int paramIndex, int optInValue )
    TA_RetCode TA_SetOptInputParamReal( TA_ParamHolder *params, unsigned int paramIndex, double optInValue )
    TA_RetCode TA_SetOutputParamIntegerPtr( TA_ParamHolder *params, unsigned int paramIndex, int  *out )
    TA_RetCode TA_SetOutputParamRealPtr( TA_ParamHolder *params,  unsigned int paramIndex, double *out )
    TA_RetCode TA_GetLookback( TA_ParamHolder *params, int *lookback )
    TA_RetCode TA_CallFunc( TA_ParamHolder *params, int startIdx,int  endIdx,int  *outBegIdx,int  *outNbElement )
 

cdef extern from "ta_libc.h":
    enum: TA_SUCCESS
    TA_RetCode TA_MA(int startIdx, int endIdx, double inReal[], int optInTimePeriod, int optInMAType, int *outBegIdx, int *outNbElement, double outReal[])
    TA_RetCode TA_Initialize()
    TA_RetCode TA_Shutdown()


class TA_Exception(Exception):
    def __init__(self,code):
        Exception.__init__(self, "TA-Lib error: %s" % code )

def check( code ):
    if code: raise TA_Exception( code )

class TA_Param:

    def __init__(self,index, name, type, flags):
        self.index = index
        self.name = name
        self.type = type
        self.flags = flags

    def __str__(self):
        return self.name.decode("utf-8")

class TA_InParam(TA_Param):

    def set_value(self,func, arg):
        if self.type == TA_Input_Real: return func.set_input_real( self.index, arg )
        if self.type == TA_Input_Integer:  return func.set_input_int( self.index, arg )
        raise TA_Exception("Unsupported param type: %s" % self.type )

class TA_OutParam(TA_Param):

    def set_value(self,func, arg):
        if self.type == TA_Output_Real: return func.set_out_real( self.index, arg )
        if self.type == TA_Output_Integer:  return func.set_out_int( self.index, arg )
        raise TA_Exception("Unsupported param type: %s" % self.type )

class TA_OptParam(TA_Param):

    def __init__(self,index,name,type, flags,display,default,hint):
        TA_Param.__init__(self,index,name,type,flags)
        self.display = display
        self.default = default
        self.hint = hint

    def set_value(self,func, arg):
        if self.type == TA_OptInput_RealRange: return func.set_opt_real( self.index, arg )
        if self.type == TA_OptInput_RealList: return func.set_opt_real( self.index, arg )
        if self.type == TA_OptInput_IntegerRange:  return func.set_opt_int( self.index, arg )
        if self.type == TA_OptInput_IntegerList:  return func.set_opt_int( self.index, arg )
        raise TA_Exception("Unsupported param type: %s" % self.type )

    def __str__(self):
        return self.name.decode("utf-8") + "=" + str(self.default)

cdef class TA_Func:

    cdef TA_FuncHandle* handle
    cdef char* name
    cdef list  params
    cdef TA_ParamHolder* ph

    def __init__(self,char* name):
        cdef TA_FuncInfo* funcInfo
        cdef TA_InputParameterInfo *inParamInfo
        cdef TA_OptInputParameterInfo *optInParamInfo
        cdef TA_OutputParameterInfo *outParamInfo

        self.name = name
        self.params = []

        check( TA_GetFuncHandle( name, &self.handle ) )
        check( TA_GetFuncInfo( self.handle, &funcInfo ) )

        for i in range( funcInfo.nbInput ):
            check( TA_GetInputParameterInfo( funcInfo.handle, i, &inParamInfo ) )
            self.params.append( TA_InParam( i, inParamInfo.paramName,inParamInfo.type, inParamInfo.flags) )

        for i in range( funcInfo.nbOutput ):
            check( TA_GetOutputParameterInfo( funcInfo.handle, i, &outParamInfo ) )
            self.params.append( TA_OutParam( i, outParamInfo.paramName,outParamInfo.type, outParamInfo.flags) )

        for i in range( funcInfo.nbOptInput ):
            check( TA_GetOptInputParameterInfo( funcInfo.handle, i, &optInParamInfo ) )
            self.params.append( TA_OptParam( i, optInParamInfo.paramName,optInParamInfo.type, optInParamInfo.flags, optInParamInfo.displayName, optInParamInfo.defaultValue, optInParamInfo.hint) )

    def get_param(self,name):
        for p in self.params:
            if p.name == name:
                return p
        raise TA_Exception("Invalid argument: %s" % name )

    def __call__(self,startIndex,endIndex,*args,**kwargs):
        cdef int outbegidx = 0
        cdef int outnbelement = 0
        check( TA_ParamHolderAlloc( self.handle, &self.ph ) )
        try:
            for i in range( len(self.params) ):
                param = self.params[i]
                if i < len(args):
                    param.set_value(self,args[i])
                    continue
                name = param.name.decode("utf-8")  
                if name in kwargs:
                    param.set_value(self,kwargs[name])
                    continue
                if isinstance( param, TA_OptParam ):
                    param.set_value(self,param.default)
                    continue
                raise TA_Exception("Required argiment not found: %s" % param )
            check( TA_CallFunc(self.ph, startIndex, endIndex, &outbegidx, &outnbelement ) )
            return( outbegidx, outnbelement )
        finally:
            check(TA_ParamHolderFree( self.ph ))

    def set_input_int(self,index,ndarray value):
        check( TA_SetInputParamIntegerPtr( self.ph, index, <int*>value.data ))

    def set_input_real(self,index,ndarray value):
        check( TA_SetInputParamRealPtr( self.ph, index, <double*>value.data ))

#    def set_input_price(index,value):
#        check(TA_SetInputParamPricePtr( TA_ParamHolder *params, unsigned int paramIndex, double *open, double *high, double *low, double *close,double *volume,double *openInterest ))

    def set_opt_int(self,index,value):
        check(TA_SetOptInputParamInteger( self.ph, index, value))

    def set_opt_real(self,index,value):
        check(TA_SetOptInputParamReal( self.ph, index,value ))

    def set_out_int(self,index,ndarray value):
        check(TA_SetOutputParamIntegerPtr(self.ph, index, <int*>value.data ))

    def set_out_real(self,index,ndarray value):
        check(TA_SetOutputParamRealPtr(self.ph, index, <double*>value.data ))

    def __str__(self):
        return self.name.decode("utf-8") + "(" + ",".join( [ str(p) for p in self.params ] ) + ")"

class TA_LIB:

    def __init__(self):
        check( TA_Initialize() )

    def __del__(self): 
        TA_Shutdown()

    def group_list(self):
        cdef TA_StringTable* table
        check( TA_GroupTableAlloc( &table ) )
        names = []
        for i in range(table.size):
            names.append( table.string[i] )
        check( TA_GroupTableFree( table ) )
        return names

    def func_list(self,group):
        cdef TA_StringTable* table
        check( TA_FuncTableAlloc( group, &table ) )
        names = []
        for i in range(table.size):
            names.append( table.string[i] )
        TA_FuncTableFree( table )
        return names

    def func(self,name):
        return TA_Func( name.encode("utf-8") )
