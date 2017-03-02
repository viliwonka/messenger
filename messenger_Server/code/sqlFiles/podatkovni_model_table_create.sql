CREATE TABLE public.user (
    username text NOT NULL,
    password_hash varchar(128) NOT NULL,
    lastonline timestamp without time zone NOT NULL,
    registertime timestamp with time zone NOT NULL,
    countrycode text NOT NULL,
    status text,
    PRIMARY KEY (username)
);

CREATE INDEX ON public.user
    (countrycode);


COMMENT ON COLUMN public.user.status
    IS 'NULL,
Kicked,
Banned';

CREATE TABLE public.friendship (
    friendshipid serial NOT NULL,
    username_1 text NOT NULL,
    username_2 text NOT NULL,
    status text NOT NULL,
    PRIMARY KEY (friendshipid)
);

CREATE INDEX ON public.friendship
    (username_1);
CREATE INDEX ON public.friendship
    (username_2);


CREATE TABLE public.message (
    messageid bigserial NOT NULL,
    chatroomid integer NOT NULL,
    username text NOT NULL,
    text text NOT NULL,
    timeposted timestamp without time zone NOT NULL,
    PRIMARY KEY (messageid)
);

CREATE INDEX ON public.message
    (chatroomid);
CREATE INDEX ON public.message
    (username);


CREATE TABLE public.country (
    code text NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (code)
);

ALTER TABLE public.country
    ADD UNIQUE (name);


CREATE TABLE public.activitydata (
    activitydataid bigserial NOT NULL,
    username text NOT NULL,
    time timestamp without time zone NOT NULL,
    ip integer NOT NULL,
    agentdata text NOT NULL,
    description text NOT NULL,
    PRIMARY KEY (activitydataid)
);

CREATE INDEX ON public.activitydata
    (username);


CREATE TABLE public.chatroom (
    chatroomid serial NOT NULL,
    name text,
    roomtype text NOT NULL,
    lastmessage integer NOT NULL,
    firstmessage integer NOT NULL,
    PRIMARY KEY (chatroomid)
);

ALTER TABLE public.chatroom
    ADD UNIQUE (name);

CREATE INDEX ON public.chatroom
    (lastmessage);
CREATE INDEX ON public.chatroom
    (firstmessage);


COMMENT ON COLUMN public.chatroom.roomtype
    IS 'Public, Private/Invite only, Invite disabled, Friend';

CREATE TABLE public.participates (
    participatesid serial NOT NULL,
    username text NOT NULL,
    chatroomid integer NOT NULL,
    userprivilege text,
    PRIMARY KEY (participatesid)
);

CREATE INDEX ON public.participates
    (username);
CREATE INDEX ON public.participates
    (chatroomid);

