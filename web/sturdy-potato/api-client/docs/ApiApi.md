# ApiApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiProjectsCreate**](ApiApi.md#apiprojectscreate) | **POST** /api/projects/ |  |
| [**apiProjectsDestroy**](ApiApi.md#apiprojectsdestroy) | **DELETE** /api/projects/{id}/ |  |
| [**apiProjectsList**](ApiApi.md#apiprojectslist) | **GET** /api/projects/ |  |
| [**apiProjectsPartialUpdate**](ApiApi.md#apiprojectspartialupdate) | **PATCH** /api/projects/{id}/ |  |
| [**apiProjectsReorderCreate**](ApiApi.md#apiprojectsreordercreate) | **POST** /api/projects/reorder/ |  |
| [**apiProjectsRetrieve**](ApiApi.md#apiprojectsretrieve) | **GET** /api/projects/{id}/ |  |
| [**apiSchemaRetrieve**](ApiApi.md#apischemaretrieve) | **GET** /api/schema/ |  |
| [**apiTasksCreate**](ApiApi.md#apitaskscreate) | **POST** /api/tasks/ |  |
| [**apiTasksDestroy**](ApiApi.md#apitasksdestroy) | **DELETE** /api/tasks/{id}/ |  |
| [**apiTasksList**](ApiApi.md#apitaskslist) | **GET** /api/tasks/ |  |
| [**apiTasksPartialUpdate**](ApiApi.md#apitaskspartialupdate) | **PATCH** /api/tasks/{id}/ |  |
| [**apiTasksReorderCreate**](ApiApi.md#apitasksreordercreate) | **POST** /api/tasks/reorder/ |  |
| [**apiTasksRetrieve**](ApiApi.md#apitasksretrieve) | **GET** /api/tasks/{id}/ |  |



## apiProjectsCreate

> ProjectSchema apiProjectsCreate(projectCreateInput)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // ProjectCreateInput (optional)
    projectCreateInput: ...,
  } satisfies ApiProjectsCreateRequest;

  try {
    const data = await api.apiProjectsCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **projectCreateInput** | [ProjectCreateInput](ProjectCreateInput.md) |  | [Optional] |

### Return type

[**ProjectSchema**](ProjectSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsDestroy

> apiProjectsDestroy(id)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // string
    id: id_example,
  } satisfies ApiProjectsDestroyRequest;

  try {
    const data = await api.apiProjectsDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `string` |  | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsList

> Array&lt;ProjectSchema&gt; apiProjectsList()



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiProjectsList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;ProjectSchema&gt;**](ProjectSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsPartialUpdate

> ProjectSchema apiProjectsPartialUpdate(id, projectUpdateInput)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // string
    id: id_example,
    // ProjectUpdateInput (optional)
    projectUpdateInput: ...,
  } satisfies ApiProjectsPartialUpdateRequest;

  try {
    const data = await api.apiProjectsPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `string` |  | [Defaults to `undefined`] |
| **projectUpdateInput** | [ProjectUpdateInput](ProjectUpdateInput.md) |  | [Optional] |

### Return type

[**ProjectSchema**](ProjectSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsReorderCreate

> apiProjectsReorderCreate()



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsReorderCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiProjectsReorderCreate();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

`void` (Empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiProjectsRetrieve

> ProjectSchema apiProjectsRetrieve(id)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiProjectsRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // string
    id: id_example,
  } satisfies ApiProjectsRetrieveRequest;

  try {
    const data = await api.apiProjectsRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `string` |  | [Defaults to `undefined`] |

### Return type

[**ProjectSchema**](ProjectSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiSchemaRetrieve

> { [key: string]: any; } apiSchemaRetrieve(format, lang)



OpenApi3 schema for this API. Format can be selected via content negotiation.  - YAML: application/vnd.oai.openapi - JSON: application/vnd.oai.openapi+json

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiSchemaRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // 'json' | 'yaml' (optional)
    format: format_example,
    // 'af' | 'ar' | 'ar-dz' | 'ast' | 'az' | 'be' | 'bg' | 'bn' | 'br' | 'bs' | 'ca' | 'ckb' | 'cs' | 'cy' | 'da' | 'de' | 'dsb' | 'el' | 'en' | 'en-au' | 'en-gb' | 'eo' | 'es' | 'es-ar' | 'es-co' | 'es-mx' | 'es-ni' | 'es-ve' | 'et' | 'eu' | 'fa' | 'fi' | 'fr' | 'fy' | 'ga' | 'gd' | 'gl' | 'he' | 'hi' | 'hr' | 'hsb' | 'ht' | 'hu' | 'hy' | 'ia' | 'id' | 'ig' | 'io' | 'is' | 'it' | 'ja' | 'ka' | 'kab' | 'kk' | 'km' | 'kn' | 'ko' | 'ky' | 'lb' | 'lt' | 'lv' | 'mk' | 'ml' | 'mn' | 'mr' | 'ms' | 'my' | 'nb' | 'ne' | 'nl' | 'nn' | 'os' | 'pa' | 'pl' | 'pt' | 'pt-br' | 'ro' | 'ru' | 'sk' | 'sl' | 'sq' | 'sr' | 'sr-latn' | 'sv' | 'sw' | 'ta' | 'te' | 'tg' | 'th' | 'tk' | 'tr' | 'tt' | 'udm' | 'ug' | 'uk' | 'ur' | 'uz' | 'vi' | 'zh-hans' | 'zh-hant' (optional)
    lang: lang_example,
  } satisfies ApiSchemaRetrieveRequest;

  try {
    const data = await api.apiSchemaRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **format** | `json`, `yaml` |  | [Optional] [Defaults to `undefined`] [Enum: json, yaml] |
| **lang** | `af`, `ar`, `ar-dz`, `ast`, `az`, `be`, `bg`, `bn`, `br`, `bs`, `ca`, `ckb`, `cs`, `cy`, `da`, `de`, `dsb`, `el`, `en`, `en-au`, `en-gb`, `eo`, `es`, `es-ar`, `es-co`, `es-mx`, `es-ni`, `es-ve`, `et`, `eu`, `fa`, `fi`, `fr`, `fy`, `ga`, `gd`, `gl`, `he`, `hi`, `hr`, `hsb`, `ht`, `hu`, `hy`, `ia`, `id`, `ig`, `io`, `is`, `it`, `ja`, `ka`, `kab`, `kk`, `km`, `kn`, `ko`, `ky`, `lb`, `lt`, `lv`, `mk`, `ml`, `mn`, `mr`, `ms`, `my`, `nb`, `ne`, `nl`, `nn`, `os`, `pa`, `pl`, `pt`, `pt-br`, `ro`, `ru`, `sk`, `sl`, `sq`, `sr`, `sr-latn`, `sv`, `sw`, `ta`, `te`, `tg`, `th`, `tk`, `tr`, `tt`, `udm`, `ug`, `uk`, `ur`, `uz`, `vi`, `zh-hans`, `zh-hant` |  | [Optional] [Defaults to `undefined`] [Enum: af, ar, ar-dz, ast, az, be, bg, bn, br, bs, ca, ckb, cs, cy, da, de, dsb, el, en, en-au, en-gb, eo, es, es-ar, es-co, es-mx, es-ni, es-ve, et, eu, fa, fi, fr, fy, ga, gd, gl, he, hi, hr, hsb, ht, hu, hy, ia, id, ig, io, is, it, ja, ka, kab, kk, km, kn, ko, ky, lb, lt, lv, mk, ml, mn, mr, ms, my, nb, ne, nl, nn, os, pa, pl, pt, pt-br, ro, ru, sk, sl, sq, sr, sr-latn, sv, sw, ta, te, tg, th, tk, tr, tt, udm, ug, uk, ur, uz, vi, zh-hans, zh-hant] |

### Return type

**{ [key: string]: any; }**

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/vnd.oai.openapi`, `application/yaml`, `application/vnd.oai.openapi+json`, `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksCreate

> TodoSchema apiTasksCreate(todoCreateInput)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // TodoCreateInput (optional)
    todoCreateInput: ...,
  } satisfies ApiTasksCreateRequest;

  try {
    const data = await api.apiTasksCreate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **todoCreateInput** | [TodoCreateInput](TodoCreateInput.md) |  | [Optional] |

### Return type

[**TodoSchema**](TodoSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksDestroy

> apiTasksDestroy(id)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksDestroyRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // string
    id: id_example,
  } satisfies ApiTasksDestroyRequest;

  try {
    const data = await api.apiTasksDestroy(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `string` |  | [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksList

> Array&lt;TodoSchema&gt; apiTasksList()



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksListRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiTasksList();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;TodoSchema&gt;**](TodoSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksPartialUpdate

> TodoSchema apiTasksPartialUpdate(id, todoUpdateInput)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksPartialUpdateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // string
    id: id_example,
    // TodoUpdateInput (optional)
    todoUpdateInput: ...,
  } satisfies ApiTasksPartialUpdateRequest;

  try {
    const data = await api.apiTasksPartialUpdate(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `string` |  | [Defaults to `undefined`] |
| **todoUpdateInput** | [TodoUpdateInput](TodoUpdateInput.md) |  | [Optional] |

### Return type

[**TodoSchema**](TodoSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksReorderCreate

> apiTasksReorderCreate()



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksReorderCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  try {
    const data = await api.apiTasksReorderCreate();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

`void` (Empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTasksRetrieve

> TodoSchema apiTasksRetrieve(id)



This is the magic.  Overrides &#x60;.as_view()&#x60; so that it takes an &#x60;actions&#x60; keyword that performs the binding of HTTP methods to actions on the Resource.  For example, to create a concrete view binding the \&#39;GET\&#39; and \&#39;POST\&#39; methods to the \&#39;alist\&#39; and \&#39;acreate\&#39; actions...  view &#x3D; MyViewSet.as_view({\&#39;get\&#39;: \&#39;alist\&#39;, \&#39;post\&#39;: \&#39;acreate\&#39;})

### Example

```ts
import {
  Configuration,
  ApiApi,
} from '';
import type { ApiTasksRetrieveRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // To configure HTTP basic authorization: basicAuth
    username: "YOUR USERNAME",
    password: "YOUR PASSWORD",
    // To configure API key authorization: cookieAuth
    apiKey: "YOUR API KEY",
  });
  const api = new ApiApi(config);

  const body = {
    // string
    id: id_example,
  } satisfies ApiTasksRetrieveRequest;

  try {
    const data = await api.apiTasksRetrieve(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **id** | `string` |  | [Defaults to `undefined`] |

### Return type

[**TodoSchema**](TodoSchema.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

