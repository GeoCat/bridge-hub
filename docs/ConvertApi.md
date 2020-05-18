# swagger_client.ConvertApi

All URIs are relative to *https://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**call_from**](ConvertApi.md#call_from) | **POST** /convert/from/{format} | Converts a given style into Geostyler
[**to**](ConvertApi.md#to) | **POST** /convert/to/{format} | Converts a Geostyler style


# **call_from**
> ResponseStyle call_from(body, format)

Converts a given style into Geostyler



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ConvertApi()
body = swagger_client.Style() # Style | The style to convert, in the format expressed in the 'format' parameter
format = 'format_example' # str | The style to convert from

try:
    # Converts a given style into Geostyler
    api_response = api_instance.call_from(body, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ConvertApi->call_from: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Style**](Style.md)| The style to convert, in the format expressed in the &#39;format&#39; parameter | 
 **format** | **str**| The style to convert from | 

### Return type

[**ResponseStyle**](ResponseStyle.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **to**
> ResponseStyle to(body, format)

Converts a Geostyler style



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ConvertApi()
body = swagger_client.Style() # Style | The Geostyler style
format = 'format_example' # str | The style to convert to

try:
    # Converts a Geostyler style
    api_response = api_instance.to(body, format)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ConvertApi->to: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Style**](Style.md)| The Geostyler style | 
 **format** | **str**| The style to convert to | 

### Return type

[**ResponseStyle**](ResponseStyle.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

