
def get_cdefs(ffibuilder):
    cdefs = []
    cdefs.append(
        """
    typedef enum {
        PARSE_NULL = 0,
        PARSE_OK,
        PARSE_INCOMPLETE,
        PARSE_ERROR,
        PARSE_EOF
    } ParseStatus;

    typedef void* (*DL_FUNC)();

    typedef unsigned int R_NativePrimitiveArgType;

    typedef struct {
        const char *name;
        DL_FUNC     fun;
        int         numArgs;
        R_NativePrimitiveArgType *types;
    } R_CMethodDef;

    typedef struct {
        const char *name;
        DL_FUNC     fun;
        int         numArgs;
    } R_CallMethodDef;

    typedef enum { FALSE = 0, TRUE } Rboolean;

    typedef struct {
        double r;
        double i;
    } Rcomplex;

    typedef enum {
        SA_NORESTORE,/* = 0 */
        SA_RESTORE,
        SA_DEFAULT,/* was === SA_RESTORE */
        SA_NOSAVE,
        SA_SAVE,
        SA_SAVEASK,
        SA_SUICIDE
    } SA_TYPE;

    typedef enum {
      Bytes = 0,
      Chars = 1,
      Width = 2
    } nchar_type;

    typedef enum {
      CE_NATIVE = 0,
      CE_UTF8   = 1,
      CE_LATIN1 = 2,
      CE_BYTES  = 3,
      CE_SYMBOL = 5,
      CE_ANY    = 99
    } cetype_t;

    typedef struct SEXPREC *SEXP;

    struct symsxp_struct {
        struct SEXPREC *pname;
        struct SEXPREC *value;
        struct SEXPREC *internal;
    };

    struct listsxp_struct {
        struct SEXPREC *carval;
        struct SEXPREC *cdrval;
        struct SEXPREC *tagval;
    };

    struct envsxp_struct {
        struct SEXPREC *frame;
        struct SEXPREC *enclos;
        struct SEXPREC *hashtab;
    };

    struct closxp_struct {
        struct SEXPREC *formals;
        struct SEXPREC *body;
        struct SEXPREC *env;
    };

    struct promsxp_struct {
        struct SEXPREC *value;
        struct SEXPREC *expr;
        struct SEXPREC *env;
    };

    typedef unsigned int SEXPTYPE;

    const unsigned int NILSXP     =  0;
    const unsigned int SYMSXP     =  1;
    const unsigned int LISTSXP    =  2;
    const unsigned int CLOSXP     =  3;
    const unsigned int ENVSXP     =  4;
    const unsigned int PROMSXP    =  5;
    const unsigned int LANGSXP    =  6;
    const unsigned int SPECIALSXP =  7;
    const unsigned int BUILTINSXP =  8;
    const unsigned int CHARSXP    =  9;
    const unsigned int LGLSXP     = 10;
    const unsigned int INTSXP     = 13;
    const unsigned int REALSXP    = 14;
    const unsigned int CPLXSXP    = 15;
    const unsigned int STRSXP     = 16;
    const unsigned int DOTSXP     = 17;
    const unsigned int ANYSXP     = 18;
    const unsigned int VECSXP     = 19;
    const unsigned int EXPRSXP    = 20;
    const unsigned int BCODESXP   = 21;
    const unsigned int EXTPTRSXP  = 22;
    const unsigned int WEAKREFSXP = 23;
    const unsigned int RAWSXP     = 24;
    const unsigned int S4SXP      = 25;

    const unsigned int NEWSXP     = 30;
    const unsigned int FREESXP    = 31;

    const unsigned int FUNSXP     = 99;

    struct sxpinfo_struct {
        SEXPTYPE type      : 5;
        unsigned int scalar: 1;
        unsigned int alt   : 1;
        unsigned int obj   : 1;
        unsigned int gp    : 16;
        unsigned int mark  : 1;
        unsigned int debug : 1;
        unsigned int trace : 1;
        unsigned int spare : 1;
        unsigned int gcgen : 1;
        unsigned int gccls : 3;
        unsigned int named : 16;
        unsigned int extra : 32;
    };

    struct primsxp_struct {
        int offset;
    };
        """)
    if ffibuilder.sizeof('size_t') > 4:
        LONG_VECTOR_SUPPORT = True
        R_XLEN_T_MAX = 4503599627370496
        R_SHORT_LEN_MAX = 2147483647
        cdefs.append("""
    typedef ptrdiff_t R_xlen_t;
        """)
    else:
        cdefs.append("""
    typedef int R_xlen_t;
        """)
    """
    struct vecsxp_struct {
        R_xlen_t length;
        R_xlen_t truelength;
    };

    typedef struct {
    %(SEXPREC_HEADER)s
        struct vecsxp_struct vecsxp;
    } VECTOR_SEXPREC, *VECSEXP;

    typedef union {
        VECTOR_SEXPREC s;
        double align;
    } SEXPREC_ALIGN;

    typedef struct SEXPREC {
    %(SEXPREC_HEADER)s
        union {
            struct primsxp_struct primsxp;
            struct symsxp_struct symsxp;
            struct listsxp_struct listsxp;
            struct envsxp_struct envsxp;
            struct closxp_struct closxp;
            struct promsxp_struct promsxp;
        } u;
    } SEXPREC;

    """

    return os.linesep.join(cdefs) % {'SEXPREC_HEADER': SEXPREC_HEADER}




ffibuilder_api = cffi.FFI()
ffibuilder_api.set_source(
    '_rinterface_cffi_api',
    get_cdefs(ffibuilder_api)
)
ffibuilder_api.cdef(
    get_cdefs(ffibuilder_api) +
    """
    extern "Python" SEXP _evaluate_in_r(SEXP);
    """)

    # ffibuilder_api.compile(verbose=True)
