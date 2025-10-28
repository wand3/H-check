// ---------------------------
// Post Response
// ---------------------------
export interface QuerySchema {
  query: string;
}
// Root Response
// ---------------------------
export interface FhirQueryResponse {
  original_query: string;
  fhir_query: FhirQuery;
  processed_results: ProcessedResults;
  execution_time: number;
}

// ---------------------------
// FHIR Query Metadata
// ---------------------------
export interface FhirQuery {
  original_query: string;
  intent: string;
  fhir_url: string;
  resource_type: string;
  filters: FhirFilters;
  search_parameters: string[];
}

export interface FhirFilters {
  age_filters: AgeFilter[];
  conditions: ConditionFilter[];
}

export interface AgeFilter {
  parameter: string;
  operator: string;
  value: number;
  search_param: string;
}

export interface ConditionFilter {
  system: string;
  code: string;
  display: string;
  search_param: string;
}

// ---------------------------
// Processed Results
// ---------------------------
export interface ProcessedResults {
  total_patients: number;
  patients: PatientSummary[];
  raw_fhir_response: FhirBundle;
}

export interface PatientSummary {
  id: string;
  conditions: string[];
  name: string;
  birthDate: string;
  age: number;
  gender: string;
}

// ---------------------------
// Simplified FHIR Bundle
// ---------------------------
export interface FhirBundle {
  resourceType: 'Bundle';
  id: string;
  meta: {
    lastUpdated: string;
  };
  type: string;
  total: number;
  link: FhirLink[];
  entry: FhirEntry[];
}

export interface FhirLink {
  relation: string;
  url: string;
}

export interface FhirEntry {
  fullUrl: string;
  resource: FhirResource;
  search: {
    mode: string;
  };
}

// ---------------------------
// FHIR Resource (Union Type)
// ---------------------------
export type FhirResource = FhirCondition | FhirPatient;

// ---------------------------
// FHIR Condition Resource
// ---------------------------
export interface FhirCondition {
  resourceType: 'Condition';
  id: string;
  meta: FhirMeta;
  language?: string;
  clinicalStatus?: FhirCodeableConcept;
  category?: FhirCodeableConcept[];
  code: FhirCodeableConcept;
  subject: FhirReference;
  onsetDateTime?: string;
}

// ---------------------------
// FHIR Patient Resource
// ---------------------------
export interface FhirPatient {
  resourceType: 'Patient';
  id: string;
  meta: FhirMeta;
  text?: {
    status: string;
    div: string;
  };
  extension?: FhirExtension[];
  identifier?: FhirIdentifier[];
  name?: FhirHumanName[];
  telecom?: FhirContactPoint[];
  gender?: string;
  birthDate?: string;
  address?: FhirAddress[];
  maritalStatus?: FhirCodeableConcept;
  contact?: FhirContact[];
  generalPractitioner?: FhirReference[];
  managingOrganization?: FhirReference;
}

// ---------------------------
// Common FHIR Subtypes
// ---------------------------
export interface FhirMeta {
  versionId?: string;
  lastUpdated: string;
  source?: string;
  profile?: string[];
}

export interface FhirCodeableConcept {
  coding?: FhirCoding[];
  text?: string;
}

export interface FhirCoding {
  system?: string;
  code?: string;
  display?: string;
}

export interface FhirReference {
  reference: string;
  type?: string;
  display?: string;
}

export interface FhirExtension {
  url: string;
  valueCoding?: FhirCoding;
  valueCodeableConcept?: FhirCodeableConcept;
  valueDate?: string;
  extension?: FhirExtension[];
  valueIdentifier?: FhirIdentifier;
  valueString?: string;
}

export interface FhirIdentifier {
  use?: string;
  type?: FhirCodeableConcept;
  system?: string;
  value?: string;
}

export interface FhirHumanName {
  use?: string;
  family?: string;
  given?: string[];
  prefix?: string[];
}

export interface FhirContactPoint {
  system?: string;
  value?: string;
  use?: string;
  rank?: number;
}

export interface FhirAddress {
  use?: string;
  type?: string;
  text?: string;
  line?: string[];
  city?: string;
  district?: string;
  state?: string;
  postalCode?: string;
  period?: { start?: string };
  extension?: FhirExtension[];
}

export interface FhirContact {
  extension?: FhirExtension[];
  relationship?: FhirCodeableConcept[];
  name?: FhirHumanName;
  telecom?: FhirContactPoint[];
  address?: FhirAddress;
  gender?: string;
}
