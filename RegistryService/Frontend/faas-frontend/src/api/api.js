export const API_BASE = "http://localhost:"
export const PORT = "8001"
export const PORT2 = "8002"
export const REGISTER = "/faas/registerFunction"
export const DELETE_FUNCTION = "/faas/deregisterFunction/"
export const GET_FUNCTIONS = "/faas/getAllFunctions"

export const UPLOAD = "/s4/uploadIntoBucket"
export const CREATE_BUCKET = "/s4/createBucket"
export const FETCH_BUCKET = "/s4/getAllFromBucket/"
export const DOWNLOAD_IMAGE = "/s4/downloadImage/"
export const DELETE_IMAGE = "/s4/deleteFromBucket"
export const DELETE_BUCKET = "/s4/deleteBucket/"



export const LOG_PREFIX = "http://10.157.3.213:5601/app/discover#/?_a=(columns:!(message,kubernetes.pod.name),filters:!(),index:'5e8dc630-fd98-11ee-b01c-e13c3a690dc4',interval:s,query:(language:kuery,query:'kubernetes.namespace:"
export const LOG_SUFFIX = "'),sort:!(!('@timestamp',desc),!(log.offset,desc)))&_g=(filters:!(),query:(language:kuery,query:''),refreshInterval:(pause:!f,value:5000),time:(from:now-60m,to:now))"
