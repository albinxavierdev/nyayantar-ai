# Nyayantar AI - API Endpoints Documentation

This document provides a comprehensive list of all available API endpoints in the Nyayantar AI RAG-SaaS application.

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 🔐 Authentication Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/signup` | Create new user account | ❌ |
| `POST` | `/api/auth/signin` | User login | ❌ |
| `POST` | `/api/auth/logout` | User logout | ✅ |
| `POST` | `/api/auth/forgot-password` | Request password reset | ❌ |
| `POST` | `/api/auth/reset-password` | Reset password with token | ❌ |
| `GET` | `/api/auth/me` | Get current user information | ✅ |
| `GET` | `/api/auth/verify-admin` | Verify admin status | ✅ |
| `POST` | `/api/auth/update` | Update user profile | ✅ |
| `POST` | `/api/auth/change-password` | Change user password | ✅ |

---

## 💬 Chat Endpoints (`/api/chat`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/chat` | Main chat endpoint (streaming) | ✅ |
| `GET` | `/api/chat/config` | Get chat configuration | ✅ |
| `POST` | `/api/chat/upload` | File upload (currently disabled) | ✅ |

---

## ⚖️ Legal Chat Endpoints (`/api/legal`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/legal` | Legal-specific chat interface | ✅ |
| `GET` | `/api/legal/stats` | Get legal chat statistics | ✅ |
| `POST` | `/api/legal/search` | Search legal knowledge base | ✅ |
| `POST` | `/api/legal/enable` | Enable legal features | ✅ |
| `POST` | `/api/legal/disable` | Disable legal features | ✅ |

---

---

## 💭 Conversation Management (`/api/conversation`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/conversation` | Create new conversation | ✅ |
| `GET` | `/api/conversation/list` | List user conversations | ✅ |
| `GET` | `/api/conversation/{conversation_id}` | Get conversation details | ✅ |
| `GET` | `/api/conversation/sharable/{conversation_id}` | Get sharable conversation | ❌ |
| `DELETE` | `/api/conversation/{conversation_id}` | Delete conversation | ✅ |
| `PATCH` | `/api/conversation/{conversation_id}/share` | Share conversation | ✅ |
| `PATCH` | `/api/conversation/{conversation_id}/summary` | Update conversation summary | ✅ |

---

## 👨‍💼 Admin Endpoints (`/api/admin`)

### User Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/users` | List all users | ✅ (Admin) |
| `GET` | `/api/admin/users/{user_id}` | Get user details | ✅ (Admin) |
| `PUT` | `/api/admin/users/{user_id}` | Update user | ✅ (Admin) |
| `DELETE` | `/api/admin/users/{user_id}` | Delete user | ✅ (Admin) |

### System Configuration
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/system-prompt` | Get system prompt | ✅ (Admin) |
| `PUT` | `/api/admin/system-prompt` | Update system prompt | ✅ (Admin) |
| `PUT` | `/api/admin/conversation-starters` | Update conversation starters | ✅ (Admin) |
| `POST` | `/api/admin/upload_data` | Upload data | ✅ (Admin) |

### Provider Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/providers` | List all providers | ✅ (Admin) |
| `POST` | `/api/admin/providers/{provider_name}/switch` | Switch to specific provider | ✅ (Admin) |
| `POST` | `/api/admin/providers/switch-to-db` | Switch to database provider | ✅ (Admin) |
| `GET` | `/api/admin/providers/current` | Get current provider | ✅ (Admin) |
| `GET` | `/api/admin/providers/status` | Get provider status | ✅ (Admin) |

### Provider Configuration
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/providers/configs` | List provider configurations | ✅ (Admin) |
| `POST` | `/api/admin/providers/configs` | Create provider configuration | ✅ (Admin) |
| `GET` | `/api/admin/providers/configs/{provider_id}` | Get provider configuration | ✅ (Admin) |
| `PUT` | `/api/admin/providers/configs/{provider_id}` | Update provider configuration | ✅ (Admin) |
| `DELETE` | `/api/admin/providers/configs/{provider_id}` | Delete provider configuration | ✅ (Admin) |
| `POST` | `/api/admin/providers/configs/{provider_id}/test` | Test provider configuration | ✅ (Admin) |
| `POST` | `/api/admin/providers/configs/{provider_id}/enable` | Enable provider | ✅ (Admin) |

---

## 📁 Static File Endpoints

| Path | Description |
|------|-------------|
| `/api/files/data/*` | Data files |
| `/api/files/output/*` | Output files from tools |

---

## 📚 Documentation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Redirects to API documentation |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |

---

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Streaming Response (Chat)
```
data: {"type": "content", "data": "AI response text"}
data: {"type": "done", "data": true}
```

---

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Internal Server Error |

---

## Rate Limiting

- Chat endpoints: 100 requests per minute per user
- Document generation: 10 requests per minute per user
- Admin endpoints: 50 requests per minute per admin

---

## Notes

- All timestamps are in UTC format
- File uploads are limited to 10MB per file
- Document generation has a 5-minute timeout
- Conversations are automatically archived after 30 days of inactivity

---

**Total Endpoints: 50+**  
**Last Updated: January 2025**
