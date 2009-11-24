--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- Name: account_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.account_id_seq OWNER TO wor;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: account; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE account (
    account_id integer DEFAULT nextval('account_id_seq'::regclass) NOT NULL,
    username character varying(32),
    password character varying(32),
    realname character varying(64),
    email character varying(64)
);


ALTER TABLE public.account OWNER TO wor;

--
-- Name: account_actor; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE account_actor (
    account_id integer NOT NULL,
    actor_id integer NOT NULL
);


ALTER TABLE public.account_actor OWNER TO wor;

--
-- Name: actor_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE actor_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.actor_id_seq OWNER TO wor;

--
-- Name: actor; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE actor (
    id integer DEFAULT nextval('actor_id_seq'::regclass) NOT NULL,
    name character varying(32),
    state bytea,
    x integer,
    y integer,
    layer character varying(32)
);


ALTER TABLE public.actor OWNER TO wor;

--
-- Name: actor_message; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE actor_message (
    id integer NOT NULL,
    stamp numeric(20,6),
    actor_id integer,
    msg_type text,
    message text
);


ALTER TABLE public.actor_message OWNER TO wor;

--
-- Name: actor_message_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE actor_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.actor_message_id_seq OWNER TO wor;

--
-- Name: actor_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wor
--

ALTER SEQUENCE actor_message_id_seq OWNED BY actor_message.id;


--
-- Name: actor_properties; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE actor_properties (
    actor_id integer NOT NULL,
    key text NOT NULL,
    type character(1),
    ivalue integer,
    fvalue double precision,
    tvalue text
);


ALTER TABLE public.actor_properties OWNER TO wor;

--
-- Name: item; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE item (
    id integer NOT NULL,
    type character varying,
    state bytea
);


ALTER TABLE public.item OWNER TO wor;

--
-- Name: item_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE item_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.item_id_seq OWNER TO wor;

--
-- Name: item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wor
--

ALTER SEQUENCE item_id_seq OWNED BY item.id;


--
-- Name: item_owner; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE item_owner (
    item_id integer NOT NULL,
    owner_type character varying NOT NULL,
    owner_id integer NOT NULL,
    container character varying NOT NULL
);


ALTER TABLE public.item_owner OWNER TO wor;

--
-- Name: item_properties; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE item_properties (
    item_id integer NOT NULL,
    key text NOT NULL,
    type character(1),
    ivalue integer,
    fvalue double precision,
    tvalue text
);


ALTER TABLE public.item_properties OWNER TO wor;

--
-- Name: location; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE location (
    id integer NOT NULL,
    x integer,
    y integer,
    layer character varying(32),
    state bytea,
    "overlay" integer
);


ALTER TABLE public.location OWNER TO wor;

--
-- Name: location_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE location_id_seq
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
-- Name: location_properties; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE location_properties (
    location_id integer NOT NULL,
    key text NOT NULL,
    type character(1),
    ivalue integer,
    fvalue double precision,
    tvalue text
);


ALTER TABLE public.location_properties OWNER TO wor;

--
-- Name: log_item_event; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE log_item_event (
    id integer NOT NULL,
    stamp numeric(12,6),
    request_id character varying(21),
    item_id integer,
    type character varying(8),
    other_id integer,
    owner_type character varying,
    owner_id integer,
    container character varying,
    orig_q integer,
    new_q integer
);


ALTER TABLE public.log_item_event OWNER TO wor;

--
-- Name: log_item_event_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE log_item_event_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.log_item_event_id_seq OWNER TO wor;

--
-- Name: log_item_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wor
--

ALTER SEQUENCE log_item_event_id_seq OWNED BY log_item_event.id;


--
-- Name: log_raw_action; Type: TABLE; Schema: public; Owner: wor; Tablespace: 
--

CREATE TABLE log_raw_action (
    id integer NOT NULL,
    stamp timestamp without time zone,
    request_id text,
    action_id text,
    action_name text,
    parameters text
);


ALTER TABLE public.log_raw_action OWNER TO wor;

--
-- Name: log_raw_action_id_seq; Type: SEQUENCE; Schema: public; Owner: wor
--

CREATE SEQUENCE log_raw_action_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.log_raw_action_id_seq OWNER TO wor;

--
-- Name: log_raw_action_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wor
--

ALTER SEQUENCE log_raw_action_id_seq OWNED BY log_raw_action.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE actor_message ALTER COLUMN id SET DEFAULT nextval('actor_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE item ALTER COLUMN id SET DEFAULT nextval('item_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE location ALTER COLUMN id SET DEFAULT nextval('location_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE log_item_event ALTER COLUMN id SET DEFAULT nextval('log_item_event_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: wor
--

ALTER TABLE log_raw_action ALTER COLUMN id SET DEFAULT nextval('log_raw_action_id_seq'::regclass);


--
-- Name: account_actor_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY account_actor
    ADD CONSTRAINT account_actor_pkey PRIMARY KEY (account_id, actor_id);


--
-- Name: account_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY account
    ADD CONSTRAINT account_pkey PRIMARY KEY (account_id);


--
-- Name: account_username; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY account
    ADD CONSTRAINT account_username UNIQUE (username);


--
-- Name: actor_id_key; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY actor
    ADD CONSTRAINT actor_id_key UNIQUE (id);


--
-- Name: actor_message_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY actor_message
    ADD CONSTRAINT actor_message_pkey PRIMARY KEY (id);


--
-- Name: actor_name; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY actor
    ADD CONSTRAINT actor_name UNIQUE (name);


--
-- Name: actor_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (id);


--
-- Name: actor_properties_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY actor_properties
    ADD CONSTRAINT actor_properties_pkey PRIMARY KEY (actor_id, key);


--
-- Name: item_owner_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY item_owner
    ADD CONSTRAINT item_owner_pkey PRIMARY KEY (item_id, owner_type, owner_id, container);


--
-- Name: item_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY item
    ADD CONSTRAINT item_pkey PRIMARY KEY (id);


--
-- Name: item_properties_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY item_properties
    ADD CONSTRAINT item_properties_pkey PRIMARY KEY (item_id, key);


--
-- Name: location_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: location_properties_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY location_properties
    ADD CONSTRAINT location_properties_pkey PRIMARY KEY (location_id, key);


--
-- Name: log_raw_action_pkey; Type: CONSTRAINT; Schema: public; Owner: wor; Tablespace: 
--

ALTER TABLE ONLY log_raw_action
    ADD CONSTRAINT log_raw_action_pkey PRIMARY KEY (id);


--
-- Name: account_actor_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY account_actor
    ADD CONSTRAINT account_actor_account_id_fkey FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE;


--
-- Name: account_actor_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY account_actor
    ADD CONSTRAINT account_actor_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES actor(id) ON DELETE CASCADE;


--
-- Name: actor_properties_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY actor_properties
    ADD CONSTRAINT actor_properties_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES actor(id) ON DELETE CASCADE;


--
-- Name: item_owner_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY item_owner
    ADD CONSTRAINT item_owner_item_id_fkey FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE;


--
-- Name: item_properties_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY item_properties
    ADD CONSTRAINT item_properties_item_id_fkey FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE;


--
-- Name: location_properties_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wor
--

ALTER TABLE ONLY location_properties
    ADD CONSTRAINT location_properties_location_id_fkey FOREIGN KEY (location_id) REFERENCES "location"(id) ON DELETE CASCADE;


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

