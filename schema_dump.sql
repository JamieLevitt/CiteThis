--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.4 (Ubuntu 17.4-1.pgdg22.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_article_last_linked(); Type: FUNCTION; Schema: public; Owner: administrator
--

CREATE FUNCTION public.update_article_last_linked() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE articles
    SET last_linked = NOW()
    WHERE url = NEW.article_url;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_article_last_linked() OWNER TO administrator;

--
-- Name: update_entity_last_linked(); Type: FUNCTION; Schema: public; Owner: administrator
--

CREATE FUNCTION public.update_entity_last_linked() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE entities
    SET last_linked = NOW()
    WHERE id = NEW.entity_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_entity_last_linked() OWNER TO administrator;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: articles; Type: TABLE; Schema: public; Owner: administrator
--

CREATE TABLE public.articles (
    url text NOT NULL,
    source text NOT NULL,
    published_date timestamp with time zone,
    last_linked timestamp with time zone
);


ALTER TABLE public.articles OWNER TO administrator;

--
-- Name: entities; Type: TABLE; Schema: public; Owner: administrator
--

CREATE TABLE public.entities (
    id text DEFAULT gen_random_uuid() NOT NULL,
    keywords text[] NOT NULL,
    wiki_url text,
    twitter_url text,
    last_linked timestamp with time zone
);


ALTER TABLE public.entities OWNER TO administrator;

--
-- Name: links_trending_topics_to_article_urls; Type: TABLE; Schema: public; Owner: administrator
--

CREATE TABLE public.links_trending_topics_to_article_urls (
    topic_id text NOT NULL,
    article_url text NOT NULL
);


ALTER TABLE public.links_trending_topics_to_article_urls OWNER TO administrator;

--
-- Name: links_trending_topics_to_entities; Type: TABLE; Schema: public; Owner: administrator
--

CREATE TABLE public.links_trending_topics_to_entities (
    topic_id text NOT NULL,
    entity_id text NOT NULL
);


ALTER TABLE public.links_trending_topics_to_entities OWNER TO administrator;

--
-- Name: trending_topics; Type: TABLE; Schema: public; Owner: administrator
--

CREATE TABLE public.trending_topics (
    topic text NOT NULL,
    started_trending date NOT NULL
);


ALTER TABLE public.trending_topics OWNER TO administrator;

--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (url);


--
-- Name: entities entities_pkey; Type: CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_pkey PRIMARY KEY (id);


--
-- Name: links_trending_topics_to_article_urls links_trending_topics_to_article_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.links_trending_topics_to_article_urls
    ADD CONSTRAINT links_trending_topics_to_article_urls_pkey PRIMARY KEY (topic_id, article_url);


--
-- Name: links_trending_topics_to_entities links_trending_topics_to_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.links_trending_topics_to_entities
    ADD CONSTRAINT links_trending_topics_to_entries_pkey PRIMARY KEY (topic_id, entity_id);


--
-- Name: trending_topics trending_topics_pkey; Type: CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.trending_topics
    ADD CONSTRAINT trending_topics_pkey PRIMARY KEY (topic);


--
-- Name: links_trending_topics_to_article_urls trigger_update_entities_last_linked; Type: TRIGGER; Schema: public; Owner: administrator
--

CREATE TRIGGER trigger_update_entities_last_linked AFTER INSERT ON public.links_trending_topics_to_article_urls FOR EACH ROW EXECUTE FUNCTION public.update_article_last_linked();


--
-- Name: links_trending_topics_to_entities trigger_update_entities_last_linked; Type: TRIGGER; Schema: public; Owner: administrator
--

CREATE TRIGGER trigger_update_entities_last_linked AFTER INSERT ON public.links_trending_topics_to_entities FOR EACH ROW EXECUTE FUNCTION public.update_entity_last_linked();


--
-- Name: links_trending_topics_to_article_urls links_trending_topics_to_article_urls_article_url_fkey; Type: FK CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.links_trending_topics_to_article_urls
    ADD CONSTRAINT links_trending_topics_to_article_urls_article_url_fkey FOREIGN KEY (article_url) REFERENCES public.articles(url) ON DELETE CASCADE;


--
-- Name: links_trending_topics_to_article_urls links_trending_topics_to_article_urls_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.links_trending_topics_to_article_urls
    ADD CONSTRAINT links_trending_topics_to_article_urls_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.trending_topics(topic) ON DELETE CASCADE;


--
-- Name: links_trending_topics_to_entities links_trending_topics_to_entries_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.links_trending_topics_to_entities
    ADD CONSTRAINT links_trending_topics_to_entries_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id) ON DELETE CASCADE;


--
-- Name: links_trending_topics_to_entities links_trending_topics_to_entries_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: administrator
--

ALTER TABLE ONLY public.links_trending_topics_to_entities
    ADD CONSTRAINT links_trending_topics_to_entries_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.trending_topics(topic) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

