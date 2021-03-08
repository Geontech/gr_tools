from gnuradio import gr, blocks
DTYPE = {
    "BYTE": gr.sizeof_char * 1,
    "FLOAT": gr.sizeof_float,
    "COMPLEX": gr.sizeof_gr_complex,
    "SHORT":gr.sizeof_short,
    "INT":gr.sizeof_int,
}
DEFAULT_FILE_SPEC = {
    "path":"",
    "type":"BYTE",
    "repeat":True,
}
DEFAULT_MESSAGE_SPEC = {
    "message": "hello world",
    "period(ms)": 300,
}
DEFAULT_OUT_SPEC = {
    "path":"",
    "type": "BYTE",
    "n_items":10000,
}
FILE_EXT = {
    "COMPLEX":".32cf",  # complex with float 32 real and imag
    "BYTE":".byte",     # bytes (8 bit int)
    "FLOAT":".32rf",    # 32 bit floats
    "INT":".32i",       # 32 bit integer
    "SHORT":".16i"      # 16 bit ints/shorts
}
