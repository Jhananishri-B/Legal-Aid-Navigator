import axios from 'axios';
import type { LegalAidRequestStatus } from '../types/status';
import type { ApplicationFormState } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token from localStorage to every request if present
client.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem('lan_auth');
    if (raw) {
      const { token } = JSON.parse(raw);
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
  } catch { /* noop */ }
  return config;
});

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: { id: string; username: string; email: string; full_name?: string; created_at: string };
}

export async function registerUser(
  username: string, email: string, password: string
): Promise<AuthResponse> {
  const res = await client.post<AuthResponse>('/api/v1/auth/register', { username, email, password });
  return res.data;
}

export async function loginUser(
  username: string, password: string
): Promise<AuthResponse> {
  const res = await client.post<AuthResponse>('/api/v1/auth/login', { username, password });
  return res.data;
}

export async function getMe(): Promise<AuthResponse['user']> {
  const res = await client.get<AuthResponse['user']>('/api/v1/auth/me');
  return res.data;
}

// ── Request creation ──────────────────────────────────────────────────────────

export interface CreateRequestPayload {
  form: ApplicationFormState;
}

export interface CreateRequestResponse {
  id: string;          // internal UUID
  request_id: string;  // display ID like LA-2025-00123
}

export async function createRequest(
  form: ApplicationFormState,
): Promise<CreateRequestResponse> {
  const res = await client.post<CreateRequestResponse>('/api/v1/requests', { form });
  return res.data;
}

// ── Request list ──────────────────────────────────────────────────────────────

export interface RequestListItem {
  id: string;
  request_id: string;
  status: string;
  current_stage: number;
  issue_type: string;
  location: string;
  created_at: string;
  updated_at: string;
}

export async function listRequests(): Promise<RequestListItem[]> {
  const res = await client.get<RequestListItem[]>('/api/v1/requests');
  return res.data;
}

// ── Status polling ────────────────────────────────────────────────────────────

export async function getRequestStatus(id: string): Promise<LegalAidRequestStatus> {
  const res = await client.get<LegalAidRequestStatus>(`/api/v1/requests/${id}/status`);
  return res.data;
}

// ── Booking approval ──────────────────────────────────────────────────────────

export async function approveBooking(
  id: string,
  slotId: string,
): Promise<{ success: boolean }> {
  const res = await client.post<{ success: boolean }>(
    `/api/v1/requests/${id}/book`,
    { slot_id: slotId },
  );
  return res.data;
}

// ── Discovery ─────────────────────────────────────────────────────────────────

export interface Authority {
  id: string;
  name: string;
  state: string;
  district: string;
  address: string;
  phone: string;
  email: string;
  website: string;
  services: string[];
  issue_types: string[];
  eligible_categories: string[];
  hours: string;
}

export async function searchAuthorities(params?: {
  state?: string;
  district?: string;
  issue_type?: string;
  category?: string;
}): Promise<{ authorities: Authority[]; total: number }> {
  const res = await client.get('/api/v1/discovery/authorities', { params });
  return res.data;
}

export async function getEligibilityCriteria(): Promise<{
  criteria: Record<string, { description: string; documents: string[]; income_limit: string }>;
}> {
  const res = await client.get('/api/v1/discovery/eligibility-criteria');
  return res.data;
}

export async function getIssueTypes(): Promise<{ issue_types: string[] }> {
  const res = await client.get('/api/v1/discovery/issue-types');
  return res.data;
}

export async function getStates(): Promise<{ states: string[] }> {
  const res = await client.get('/api/v1/discovery/states');
  return res.data;
}

// ── Local storage helpers for request ID ─────────────────────────────────────

export const REQUEST_ID_KEY = 'lan_request_id';
export const SUBMITTED_FORM_KEY = 'lan_submitted_form';
export const SUBMITTED_AT_KEY = 'lan_submitted_at';
export const LOCAL_REQUEST_ID_KEY = 'lan_local_request_id';

export function saveRequestId(id: string) {
  localStorage.setItem(REQUEST_ID_KEY, id);
}

export function loadRequestId(): string | null {
  return localStorage.getItem(REQUEST_ID_KEY);
}

export function clearRequestId() {
  localStorage.removeItem(REQUEST_ID_KEY);
}

export function saveSubmittedForm(form: ApplicationFormState, localRequestId: string) {
  localStorage.setItem(SUBMITTED_FORM_KEY, JSON.stringify(form));
  localStorage.setItem(SUBMITTED_AT_KEY, new Date().toISOString());
  localStorage.setItem(LOCAL_REQUEST_ID_KEY, localRequestId);
}

export function loadSubmittedForm(): { form: ApplicationFormState; submittedAt: string; localRequestId: string } | null {
  try {
    const raw = localStorage.getItem(SUBMITTED_FORM_KEY);
    const submittedAt = localStorage.getItem(SUBMITTED_AT_KEY);
    const localRequestId = localStorage.getItem(LOCAL_REQUEST_ID_KEY);
    if (raw && submittedAt && localRequestId) {
      return { form: JSON.parse(raw), submittedAt, localRequestId };
    }
  } catch { /* noop */ }
  return null;
}

export function clearSubmittedForm() {
  localStorage.removeItem(SUBMITTED_FORM_KEY);
  localStorage.removeItem(SUBMITTED_AT_KEY);
  localStorage.removeItem(LOCAL_REQUEST_ID_KEY);
}
