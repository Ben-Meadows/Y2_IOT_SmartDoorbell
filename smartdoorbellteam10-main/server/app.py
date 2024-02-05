import bottle
import routes

bottle.BaseRequest.MEMFILE_MAX = 4097 * 4096

bottle.run(host="localhost", port=8081, debug=True)
