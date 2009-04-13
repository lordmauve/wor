--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: player; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE player (
    id integer NOT NULL,
    username character varying(32),
    password character varying(32),
    state text
);


ALTER TABLE public.player OWNER TO wor;

--
-- Name: player_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE player_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.player_id_seq OWNER TO wor;

--
-- Name: player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wor
--

ALTER SEQUENCE player_id_seq OWNED BY player.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE player ALTER COLUMN id SET DEFAULT nextval('player_id_seq'::regclass);


--
-- Name: player_id_key; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY player
    ADD CONSTRAINT player_id_key UNIQUE (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

