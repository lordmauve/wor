--
-- PostgreSQL database dump
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: location; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE location (
    id integer NOT NULL,
    x integer NOT NULL,
    y integer NOT NULL,
    layer character varying(32) NOT NULL,
    state bytea,
    override integer
);


ALTER TABLE public.location OWNER TO wor;

--
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.location_id_seq OWNER TO wor;

--
-- Name: location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wor
--

ALTER SEQUENCE location_id_seq OWNED BY location.id;


--
-- Name: player; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE player (
    id integer NOT NULL,
    username character varying(32),
    "password" character varying(32),
    state bytea
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
-- Name: player_properties; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE player_properties (
    player_id integer NOT NULL,
    "key" text NOT NULL,
    "type" character(1),
    ivalue integer,
    fvalue double precision,
    tvalue text,
    bvalue bytea
);


ALTER TABLE public.player_properties OWNER TO wor;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE location ALTER COLUMN id SET DEFAULT nextval('location_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE player ALTER COLUMN id SET DEFAULT nextval('player_id_seq'::regclass);


--
-- Name: location_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: location_x_key; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_x_key UNIQUE (x, y, layer, override);


--
-- Name: player_id_key; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY player
    ADD CONSTRAINT player_id_key UNIQUE (id);


--
-- Name: player_properties_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY player_properties
    ADD CONSTRAINT player_properties_pkey PRIMARY KEY (player_id, "key");


--
-- Name: player_properties_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY player_properties
    ADD CONSTRAINT player_properties_player_id_fkey FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE;


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

