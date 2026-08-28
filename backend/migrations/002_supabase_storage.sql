-- ============================================================================
-- VaniPath - Supabase Storage Buckets
-- ============================================================================
-- Run this AFTER 001_supabase_schema.sql in Supabase SQL Editor.
-- Creates storage buckets for audio, worksheets, flashcards, curriculum.
-- ============================================================================

-- Create storage buckets (Supabase SQL API)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  (
    'vanipath-audio',
    'vanipath-audio',
    true,  -- public read for audio playback
    10485760,  -- 10 MB
    ARRAY['audio/wav','audio/mp3','audio/ogg','audio/m4a','audio/webm']::text[]
  ),
  (
    'vanipath-worksheets',
    'vanipath-worksheets',
    false,  -- private, accessed via signed URLs
    20971520,  -- 20 MB
    ARRAY['application/pdf','image/png','image/jpeg']::text[]
  ),
  (
    'vanipath-flashcards',
    'vanipath-flashcards',
    true,  -- public read for images
    5242880,  -- 5 MB
    ARRAY['image/png','image/jpeg','image/webp','image/svg+xml']::text[]
  ),
  (
    'vanipath-curriculum',
    'vanipath-curriculum',
    false,  -- private content packs
    52428800,  -- 50 MB
    ARRAY['application/json','application/pdf','image/png','image/jpeg']::text[]
  )
ON CONFLICT (id) DO UPDATE SET
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- RLS policies for storage objects
-- Use DROP IF EXISTS + CREATE for compatibility with all PostgreSQL versions

-- Public read for audio and flashcard buckets
DROP POLICY IF EXISTS "audio_public_read" ON storage.objects;
CREATE POLICY "audio_public_read"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'vanipath-audio');

DROP POLICY IF EXISTS "flashcards_public_read" ON storage.objects;
CREATE POLICY "flashcards_public_read"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'vanipath-flashcards');

-- Authenticated upload for all buckets
DROP POLICY IF EXISTS "auth_upload_audio" ON storage.objects;
CREATE POLICY "auth_upload_audio"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'vanipath-audio' AND auth.role() = 'authenticated');

DROP POLICY IF EXISTS "auth_upload_worksheets" ON storage.objects;
CREATE POLICY "auth_upload_worksheets"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'vanipath-worksheets' AND auth.role() = 'authenticated');

DROP POLICY IF EXISTS "auth_upload_flashcards" ON storage.objects;
CREATE POLICY "auth_upload_flashcards"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'vanipath-flashcards' AND auth.role() = 'authenticated');

DROP POLICY IF EXISTS "auth_upload_curriculum" ON storage.objects;
CREATE POLICY "auth_upload_curriculum"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'vanipath-curriculum' AND auth.role() = 'authenticated');
