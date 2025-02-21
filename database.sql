--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Postgres.app)
-- Dumped by pg_dump version 17.2 (Postgres.app)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bills; Type: TABLE; Schema: public; Owner: juaneulogio
--

CREATE TABLE public.bills (
    billnumber character varying(255),
    billid integer NOT NULL,
    billstatusdate date,
    billstatus integer,
    billtitle text,
    billdescription text,
    aisummary text
);



ALTER TABLE public.bills OWNER TO juaneulogio;

--
-- Data for Name: bills; Type: TABLE DATA; Schema: public; Owner: juaneulogio
--

COPY public.bills (billnumber, billid, billstatusdate, billstatus, billtitle, billdescription, aisummary) FROM stdin;
\.


--
-- Name: bills bills_pkey; Type: CONSTRAINT; Schema: public; Owner: juaneulogio
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_pkey PRIMARY KEY (billid);


--
-- PostgreSQL database dump complete
--

