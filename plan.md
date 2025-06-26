# Implementation Plan for Hermes System Features

## Overview

This plan outlines the implementation of all requested features for the Hermes system, including database changes, API modifications, and frontend updates.

## 1. Access via Link for Different Evaluators (Adjudicators)

### 1.1 Database Changes

- **New Model**: `TestSession`
  ```python
  class TestSession(models.Model):
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      active_test = models.ForeignKey(ActiveTest, on_delete=models.CASCADE)
      created_by = models.ForeignKey(User, on_delete=models.CASCADE)
      created_at = models.DateTimeField(auto_now_add=True)
      expires_at = models.DateTimeField()
      is_active = models.BooleanField(default=True)
      access_code = models.CharField(max_length=8, unique=True)  # Short code for easy sharing
  ```

### 1.2 API Endpoints

- `POST /test-sessions/` - Create new test session
- `GET /test-sessions/{access_code}/` - Validate access code
- `GET /test-sessions/{session_id}/profiles/` - Get profiles for session
- `POST /test-sessions/{session_id}/results/` - Submit results for session

### 1.3 Frontend Changes

- New component: `TestSessionManager.tsx`
- Session creation interface for team admins
- Access code sharing functionality
- Session-specific test interfaces

## 2. Profile -> Person Rename

### 2.1 Database Migration

- Rename `Profile` model to `Person`
- Update all foreign key references
- Update all related field names

### 2.2 API Changes

- Update all endpoint URLs from `/profiles/` to `/persons/`
- Update schema names from `ProfileSchema` to `PersonSchema`
- Update all response types

### 2.3 Frontend Changes

- Update all component names and imports
- Update all API calls
- Update all type definitions
- Update all UI text from "Profile" to "Person"

## 3. Time-Dependent Characteristics (Height + Weight)

### 3.1 Database Changes

- **New Model**: `PersonMeasurement`
  ```python
  class PersonMeasurement(models.Model):
      person = models.ForeignKey(Person, on_delete=models.CASCADE)
      measurement_date = models.DateField()
      height = models.FloatField()
      weight = models.FloatField()
      recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
      notes = models.TextField(blank=True)
  ```

### 3.2 API Endpoints

- `GET /persons/{person_id}/measurements/` - Get measurement history
- `POST /persons/{person_id}/measurements/` - Add new measurement
- `GET /persons/{person_id}/measurements/latest/` - Get latest measurement

### 3.3 Frontend Changes

- New component: `PersonMeasurementHistory.tsx`
- Measurement tracking interface
- Charts showing height/weight over time
- Integration with test forms to use latest measurements

## 4. Beep Test Number Assignment

### 4.1 Database Changes

- Add field to `TestResult` model:
  ```python
  beep_test_number = models.IntegerField(null=True, blank=True)
  ```

### 4.2 API Changes

- Update beep test endpoints to include number assignment
- Add endpoint: `GET /beep-test/numbers/{active_test_id}/` - Get assigned numbers

### 4.3 Frontend Changes

- Update `BeepTestBatch.tsx` to include number assignment
- Add number input field to batch interface
- Add sorting by number in results display
- Add number validation (unique per test session)

## 5. Minimum Value Handling (1 point for values below minimum)

### 5.1 Backend Changes

- Update score calculation functions in `score_tables.py`
- Modify all test score calculations to return minimum 1 point
- Update validation logic

### 5.2 Frontend Changes

- Update score display to show minimum 1 point
- Add visual indicators for minimum scores
- Update score calculation preview

## 6. Input Format Hints

### 6.1 Frontend Changes

- Add `placeholder` attributes to all numeric inputs
- Add `title` attributes with format hints
- Add helper text below inputs
- Examples:
  - "Enter time in seconds (e.g., 12.5)"
  - "Enter distance in meters (e.g., 5.2)"
  - "Enter level number (e.g., 5)"

### 6.2 Component Updates

- Update all test form components
- Add format validation with helpful error messages
- Add input masks where appropriate

## 7. Y Test Improvements

### 7.1 Frontend Changes

- **Update Y Test Labels**:
  - `y_test_ll_front` → "Left Leg - Front (Left Leg Standing)"
  - `y_test_ll_left` → "Left Leg - Left (Left Leg Standing)"
  - `y_test_ll_right` → "Left Leg - Right (Left Leg Standing)"
  - `y_test_rl_front` → "Right Leg - Front (Right Leg Standing)"
  - `y_test_rl_right` → "Right Leg - Right (Right Leg Standing)"
  - `y_test_rl_left` → "Right Leg - Left (Right Leg Standing)"
  - `y_test_la_left` → "Left Arm - Left (Left Arm Propped)"
  - `y_test_la_front` → "Left Arm - Front (Left Arm Propped)"
  - `y_test_la_back` → "Left Arm - Back (Left Arm Propped)"
  - `y_test_ra_right` → "Right Arm - Right (Right Arm Propped)"
  - `y_test_ra_front` → "Right Arm - Front (Right Arm Propped)"
  - `y_test_ra_back` → "Right Arm - Back (Right Arm Propped)"

### 7.2 UI Improvements

- Add visual diagram showing test positions
- Add tooltips explaining each measurement
- Group measurements by standing leg
- Add validation for logical consistency

## 8. Import Database of Participants

### 8.1 Backend Changes

- **New API Endpoint**: `POST /persons/import/`
- Support for CSV/Excel file upload
- Partial data handling (missing fields)
- Validation and error reporting
- Batch processing with progress tracking

### 8.2 Frontend Changes

- New component: `PersonImport.tsx`
- File upload interface
- Column mapping interface
- Preview of imported data
- Error handling and reporting
- Progress tracking

### 8.3 Import Features

- Support for required fields: name, surname
- Optional fields: date_of_birth, gender, height, weight
- Automatic age calculation from date of birth
- Duplicate detection and handling
- Validation rules enforcement

## 9. Gender and Date of Birth Collection

### 9.1 Database Changes

- Add fields to track missing data:
  ```python
  class Person(models.Model):
      # ... existing fields ...
      gender_required = models.BooleanField(default=False)
      date_of_birth_required = models.BooleanField(default=False)
  ```

### 9.2 Frontend Changes

- **New Component**: `PersonDataCollection.tsx`
- Modal/dialog for collecting missing data
- Integration with test forms
- Validation and error handling

### 9.3 Flow Implementation

- Check for missing data before test submission
- Show data collection form if needed
- Update person record with collected data
- Continue with test after data collection

## Implementation Priority

### Phase 1 (High Priority)

1. Profile → Person rename
2. Input format hints
3. Y Test label improvements
4. Minimum value handling

### Phase 2 (Medium Priority)

1. Time-dependent characteristics
2. Beep test number assignment
3. Gender and date of birth collection

### Phase 3 (Low Priority)

1. Access via link for evaluators
2. Import database functionality

## Technical Considerations

### Database Migrations

- Create comprehensive migration plan
- Test migrations on development data
- Plan rollback strategy
- Consider data integrity during transitions

### API Versioning

- Consider API versioning for breaking changes
- Maintain backward compatibility where possible
- Document all API changes

### Frontend Compatibility

- Update all TypeScript interfaces
- Update all API calls
- Update all component props
- Update all routing

### Testing Strategy

- Unit tests for all new functionality
- Integration tests for API changes
- End-to-end tests for user flows
- Performance testing for import functionality

## File Structure Changes

### New Files

```
src/
├── components/
│   ├── PersonMeasurementHistory.tsx
│   ├── TestSessionManager.tsx
│   ├── PersonImport.tsx
│   └── PersonDataCollection.tsx
├── pages/
│   ├── management/
│   │   └── TestSessions.tsx
│   └── tests/
│       └── SessionTest.tsx
└── utils/
    └── importHelpers.ts
```

### Modified Files

- All test components (rename Profile → Person)
- All API calls and types
- All routing configurations
- All form validation schemas

## Estimated Timeline

- **Phase 1**: 2-3 weeks
- **Phase 2**: 3-4 weeks
- **Phase 3**: 2-3 weeks
- **Total**: 7-10 weeks

## Risk Mitigation

1. **Data Migration**: Create comprehensive backup strategy
2. **API Breaking Changes**: Implement proper versioning
3. **User Experience**: Maintain familiar interface during transitions
4. **Performance**: Monitor import functionality performance
5. **Testing**: Comprehensive testing at each phase
