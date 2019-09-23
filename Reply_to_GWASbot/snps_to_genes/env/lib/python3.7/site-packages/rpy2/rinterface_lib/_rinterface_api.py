from _rinterface_cffi_api import ffi

@ffi.def_extern()
def _evaluate_in_r(rargs):
    # An uncaught exception in the boby of this function would
    # result in a segfault. we wrap it in a try-except an report
    # exceptions as logs.

    rlib = openrlib.rlib

    try:
        rargs = rlib.CDR(rargs)
        cdata = rlib.CAR(rargs)
        if (_TYPEOF(cdata) != rlib.EXTPTRSXP):
            # TODO: also check tag
            #    (rlib.R_ExternalPtrTag(sexp) == '.Python')
            logger.error('The fist item is not an R external pointer.')
            return rlib.R_NilValue
        handle = rlib.R_ExternalPtrAddr(cdata)
        func = ffi.from_handle(handle)

        pyargs = []
        pykwargs = {}
        rargs = rlib.CDR(rargs)
        while rargs != rlib.R_NilValue:
            cdata = rlib.CAR(rargs)
            if rlib.Rf_isNull(rlib.TAG(rargs)):
                # Unnamed argument
                pyargs.append(conversion._cdata_to_rinterface(cdata))
            else:
                # Named arguments
                name = conversion._cchar_to_str(
                    rlib.R_CHAR(rlib.PRINTNAME(rlib.TAG(rargs)))
                )
                pykwargs[name] = conversion._cdata_to_rinterface(cdata)
            rargs = rlib.CDR(rargs)

        res = func(*pyargs, **pykwargs)
        # The object is whatever the "rternalized" function `func`
        # is returning and we need to cast that result into a SEXP
        # that R's C API can handle. At the same time we need to ensure
        # that the R is:
        # - protected from garbage collection long enough to let the R
        #   code that called the rternalized function complete.
        # - eventually its memory is freed to prevent a leak.
        # To that end, we create a SEXP object to be returned that is
        # not managed by rpy2, leaving the object's lifespan under R's
        # sole control.
        if (
                hasattr(res, '_sexpobject') and
                isinstance(res._sexpobject, SexpCapsule)
        ):
            return res._sexpobject._cdata
        else:
            return conversion._python_to_cdata(res)
    except Exception as e:
        logger.error('%s: %s' % (type(e), e))
        return rlib.R_NilValue

