# ChatApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiChatCreate**](ChatApi.md#apichatcreate) | **POST** /api/chat/ | Chat |



## apiChatCreate

> apiChatCreate(chatRequest, xWorkspaceId)

Chat

Chat with the local model, streaming tokens and tool activity as SSE.  The conversation is replayed by the client on each turn. Authorization is the normal workspace-membership check; the caller\&#39;s token is forwarded to the MCP server so the model\&#39;s tool calls run as that user.

### Example

```ts
import {
  Configuration,
  ChatApi,
} from '';
import type { ApiChatCreateRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ChatApi(config);

  const body = {
    // ChatRequest
    chatRequest: ...,
    // number (optional)
    xWorkspaceId: 56,
  } satisfies ApiChatCreateRequest;

  try {
    const data = await api.apiChatCreate(body);
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
| **chatRequest** | [ChatRequest](ChatRequest.md) |  | |
| **xWorkspaceId** | `number` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `text/event-stream`, `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

