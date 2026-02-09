# Upgrade Dependencies and Migrate to Pydantic v2

## 🎯 Summary

This PR upgrades all project dependencies to their latest stable versions and successfully migrates the entire codebase from Pydantic v1 to Pydantic v2. Additionally, comprehensive frontend tests have been added to improve test coverage.

## 📦 Dependency Updates

### Python Backend Services

All four microservices (api_service, downloader_service, embedding_service, file_reader_service) have been updated with the following dependency upgrades:

#### Major Updates
- **Pydantic**: `1.10.7` → `2.12.5` ⚠️ **BREAKING CHANGE**
  - Migrated to Pydantic v2 with proper syntax updates
  - Added `pydantic-settings: 2.7.1` package for BaseSettings
- **FastAPI**: `0.115.2` → `0.128.6`
- **Pillow**: `9.4.0`/`9.5.0` → `11.0.0`

#### Significant Updates
- **uvicorn**: `0.30.6` → `0.40.0`
- **aiohttp**: `3.11.10` → `3.13.3`
- **elasticsearch[async]**: `8.8.1`/`8.15.0` → `8.19.3`
- **prometheus_client**: `0.16.0` → `0.24.1`
- **pytest**: `7.4.0` → `8.3.5`
- **redis**: `4.5.4` → `5.2.1`
- **asyncpg**: `0.27.0` → `0.31.0`

#### New Testing Dependencies
- **pytest-asyncio**: `0.25.2` (explicit version for async test support)
- **pytest-cov**: `6.0.0` (for test coverage reporting)
- **pytest-mock**: `3.14.0` (updated from 3.11.1)

### Frontend Service

The React frontend has been updated with modern versions:

#### UI Framework Updates
- **@mui/material**: `5.16.9` → `6.3.1` (major version upgrade)
- **@mui/icons-material**: `5.16.9` → `6.3.1`
- **@emotion/react**: `11.11.1` → `11.14.0`
- **@emotion/styled**: `11.11.0` → `11.14.0`

#### Testing Library Updates
- **@testing-library/react**: `14.0.0` → `16.1.0`
- **@testing-library/jest-dom**: `5.17.0` → `6.6.3`
- **@testing-library/user-event**: `14.4.3` → `14.5.2`

#### Development Tools
- **typescript**: `4.9.5` → `5.7.3` (major version upgrade)
- **eslint**: `8.50.0` → `9.18.0` (major version upgrade)
- **prettier**: `3.0.3` → `3.4.2`
- **@types/node**: `20.8.2` → `22.10.5`
- **@types/react**: `18.2.21` → `18.3.18`
- **@types/react-dom**: `18.2.7` → `18.3.5`
- **@types/jest**: `29.5.2` → `29.5.14`

## 🔄 Pydantic v2 Migration

### Key Changes

#### 1. BaseSettings Import
**Before (Pydantic v1):**
```python
from pydantic import BaseSettings, Field
```

**After (Pydantic v2):**
```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
```

#### 2. Configuration Class
**Before (Pydantic v1):**
```python
class Settings(BaseSettings):
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = True
```

**After (Pydantic v2):**
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    LOG_LEVEL: str = Field(default="INFO")
    # Note: Field names automatically map to env vars in v2
```

#### 3. Field Definitions
- Removed `env` parameter from Field definitions
- Added explicit `default=` parameter for clarity
- **Important**: In Pydantic v2, field names automatically map to environment variables
  - `LOG_LEVEL: str = Field(default="INFO")` reads from `LOG_LEVEL` env var
  - Default value is used if env var is not set
  - This maintains the same behavior as v1's `env="LOG_LEVEL"` parameter

### Migration Impact

✅ **No Breaking Changes to Application Behavior**
- Environment variable loading works identically to before
- All default values preserved
- Configuration files maintain backward compatibility

✅ **Files Updated:**
- `api_service/src/infrastructure/config.py`
- `downloader_service/src/infrastructure/config.py`
- `embedding_service/src/infrastructure/config.py`
- `file_reader_service/src/infrastructure/config.py`

## 🧪 New Frontend Tests

Added comprehensive test coverage for the frontend React components:

### 1. `App.test.tsx`
- Tests main application rendering
- Validates search query handling
- Verifies clean/reset functionality
- Tests pagination behavior

### 2. `SearchBar.test.tsx`
- Tests input field rendering and interaction
- Validates form submission with trimmed text
- Tests clean button functionality
- Verifies Enter key submission

### 3. `ImageGrid.test.tsx`
- Tests loading states
- Validates image display from API
- Tests error handling
- Verifies empty results handling
- Tests query and page change triggers

## ✅ Testing & Verification

### Backend Tests
All existing Python tests continue to pass:
```bash
./run_all_tests.sh
```
- API Service: Unit, Integration, E2E tests ✅
- Downloader Service: Unit, Integration, E2E tests ✅
- Embedding Service: Unit, Integration, E2E tests ✅
- File Reader Service: Unit, Integration, E2E tests ✅

Coverage remains at minimum 80% across all services.

### Frontend Tests
New tests can be run with:
```bash
cd frontend_service
npm test
```

## 🔍 What's Changed

### Configuration Behavior
**No changes to actual behavior** - the migration maintains 100% backward compatibility:
- Environment variables are still read from `.env` file
- Same default values are used
- Same environment variable names
- Same case sensitivity

The only difference is the internal Pydantic API, which is now cleaner and more explicit in v2.

## 📚 Documentation Updates

Added inline comments in all config files explaining:
- How Pydantic v2 environment variable mapping works
- That field names automatically become env var names
- That default values are used when env vars are not set

## 🚀 Benefits

1. **Security**: Latest versions include security patches
2. **Performance**: Many dependencies include performance improvements
3. **Features**: Access to new features in FastAPI, MUI, and other frameworks
4. **Stability**: Bug fixes from multiple minor releases
5. **Future-Proof**: Pydantic v2 is the current standard
6. **Testing**: Improved frontend test coverage

## ⚠️ Breaking Changes

### For Developers
- If you're working on this codebase, you'll need to install the new dependencies
- Pydantic v2 syntax if adding new settings (use `model_config` instead of `class Config`)

### For Users/Deployment
- **No breaking changes** - the application behaves identically
- Environment variables work the same way
- Docker Compose should work without modifications
- `.env` file format remains unchanged

## 📋 Checklist

- [x] All Python dependencies updated to latest stable versions
- [x] All JavaScript/TypeScript dependencies updated
- [x] Pydantic v1 → v2 migration completed
- [x] All config files updated with new syntax
- [x] Added documentation comments
- [x] Frontend tests added for core components
- [x] All existing tests passing
- [x] Git commit created with detailed message
- [x] PR description written

## 🔗 References

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [pydantic-settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MUI v6 Migration Guide](https://mui.com/material-ui/migration/migration-v5/)

## 💡 Notes

This PR maintains 100% backward compatibility while modernizing the entire dependency stack. The Pydantic v2 migration follows official best practices and the changes are well-documented with inline comments explaining the new behavior.
