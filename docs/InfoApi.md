# swagger_client.InfoApi

All URIs are relative to *https://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**info_get**](InfoApi.md#info_get) | **GET** /info | Returns server information


# **info_get**
> Info info_get()

Returns server information

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.InfoApi()

try:
    # Returns server information
    api_response = api_instance.info_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling InfoApi->info_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Info**](Info.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

