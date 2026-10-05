-- Opportunity Engine v0.3 - PostgreSQL / Supabase schema
create extension if not exists pgcrypto;

create table if not exists sources (
  id uuid primary key default gen_random_uuid(),
  source_key text unique not null,
  source_type text not null,
  base_url text,
  authority_level text,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists raw_events (
  event_key text primary key,
  source_key text not null,
  external_id text,
  source_url text not null,
  published_at timestamptz,
  title text not null,
  raw_payload jsonb not null,
  content_hash text,
  ingested_at timestamptz not null default now()
);
create index if not exists raw_events_published_idx on raw_events(published_at);
create index if not exists raw_events_payload_gin on raw_events using gin(raw_payload);

create table if not exists projects (
  project_id text primary key,
  canonical_name text not null,
  country text,
  region text,
  city text,
  latitude double precision,
  longitude double precision,
  project_type text,
  phase text,
  project_confidence numeric(5,2),
  value_eur numeric,
  funding_eur numeric,
  first_seen_at timestamptz default now(),
  last_seen_at timestamptz default now()
);
create index if not exists projects_location_idx on projects(country,region,city);
create index if not exists projects_phase_idx on projects(phase);

create table if not exists project_events (
  project_id text references projects(project_id) on delete cascade,
  event_key text references raw_events(event_key) on delete cascade,
  resolution_score numeric(5,4),
  resolution_method text,
  primary key(project_id,event_key)
);

create table if not exists project_trades (
  project_id text references projects(project_id) on delete cascade,
  trade_code text not null,
  trade_confidence numeric(5,2) not null,
  timing_score numeric(5,2),
  evidence jsonb default '{}'::jsonb,
  primary key(project_id,trade_code)
);

create table if not exists companies (
  company_id uuid primary key default gen_random_uuid(),
  name text not null,
  country text,
  latitude double precision,
  longitude double precision,
  radius_km numeric,
  min_project_eur numeric,
  max_project_eur numeric,
  profile jsonb default '{}'::jsonb
);

create table if not exists company_trades (
  company_id uuid references companies(company_id) on delete cascade,
  trade_code text not null,
  primary key(company_id,trade_code)
);

create table if not exists matches (
  company_id uuid references companies(company_id) on delete cascade,
  project_id text references projects(project_id) on delete cascade,
  trade_code text not null,
  score numeric(5,2) not null,
  band text not null check (band in ('HOT','UPCOMING','EARLY','HIDDEN')),
  distance_km numeric,
  explanation jsonb default '{}'::jsonb,
  calculated_at timestamptz not null default now(),
  primary key(company_id,project_id,trade_code)
);


-- v0.6 lifecycle edges and human review
create table if not exists lifecycle_edges (
  project_id text references projects(project_id) on delete cascade,
  event_key text references raw_events(event_key) on delete cascade,
  phase text not null,
  link_score numeric(5,4),
  link_method text not null,
  evidence jsonb default '{}'::jsonb,
  primary key(project_id,event_key)
);
create index if not exists lifecycle_edges_phase_idx on lifecycle_edges(phase);

create table if not exists resolution_review_queue (
  id bigserial primary key,
  project_id text,
  event_key text,
  candidate_score numeric(5,4),
  evidence jsonb default '{}'::jsonb,
  status text not null default 'open',
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);
