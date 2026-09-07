# Email Header and Authentication Realism Specification

> **Names in this specification are placeholders.** The examples below use kestrelbrook.example, Sentrywick MailGate, Larchwind Mail, Quillpost and Marrowdale Mail because they were written before the corpus organization was chosen. The corpus itself uses Pellgrave Mechanical Group (pellgrave.example), the gateway product Sentrywick Gateway with its Sentrywick Store mailbox server, the webmail provider Lanternmail (lanternmail.example) and the bulk provider Sendbarrow Mail. The rules do not change; only the names do. See `phase0-corpus-design.md` section 2 for the organization and section 14, decision 8, for the names kept.

**Course:** Agentic AI and Security Operations (ITSY1377_builder)
**Applies to:** every `.eml` file in `builder/corpus/emails/`
**Status:** Phase 0 draft for approval

This document tells the corpus generator how to write email headers the way a real gateway writes them, while staying fully synthetic. Every rule carries a citation; section 10 enforces them.

Names in examples are placeholders (organization `kestrelbrook.example`, fictional gateway product "Sentrywick Gateway", bulk-mail provider `larchwind-mail.example`, webmail provider `quillpost.example`); the corpus design may rename them as long as section 6 holds.

## 1. Message format (RFC 5322)

A message is a header section, a blank line, and a body. Rules, each with its RFC 5322 section (URL `https://www.rfc-editor.org/rfc/rfc5322.html#section-N`):

- Every line ends with CRLF, carriage return then line feed. Sec. 2.1.
- A line is at most 998 characters and should be at most 78, not counting CRLF. Sec. 2.1.1.
- Long header fields fold by inserting CRLF before existing white space; continuation lines start with a space or tab. Sec. 2.2.3.
- `Date` and `From` are the only required fields; every message should also carry `Message-ID`. Sec. 3.6.
- `Date` uses a numeric zone, `+HHMM` or `-HHMM`, with an optional correct day-of-week. Sec. 3.3.
- `Sender` appears only when `From` lists more than one mailbox or a system sends on a person's behalf; `Reply-To` is optional. Sec. 3.6.2.
- `Message-ID` is `<id-left@id-right>`; id-right should be a domain the generator controls. Sec. 3.6.4.
- A reply carries `In-Reply-To` with the parent's Message-ID, and `References` with the parent's References followed by the parent's Message-ID. Sec. 3.6.4.
- Trace fields (`Return-Path`, `Received`) are never reordered and sit in a block at the top, most recent first. Sec. 3.6.7.
- Undefined field names are permitted as optional fields, which allows `X-` and vendor headers. Sec. 3.6.8.

Worked example (an internal reply; its `Received` block is in section 7):

```
Date: Tue, 14 Apr 2026 09:12:41 -0500
From: Dana Okafor <d.okafor@kestrelbrook.example>
To: Marisol Reyes <m.reyes@kestrelbrook.example>
Cc: AP Shared Mailbox <ap-team@kestrelbrook.example>
Reply-To: ap-team@kestrelbrook.example
Subject: Re: Vendor payment run for 4/17
Message-ID: <20260414141241.7f3a9c1e2b04@mail.kestrelbrook.example>
In-Reply-To: <20260413221530.a81c0d55e9f2@mail.kestrelbrook.example>
References: <20260413221530.a81c0d55e9f2@mail.kestrelbrook.example>
```

Convention: `Message-ID` left side is the UTC timestamp plus twelve hex digits; right side is the originating mail host.

## 2. MIME (RFC 2045, 2046, 2047, 2183)

MIME (Multipurpose Internet Mail Extensions) is the rule set for bodies beyond plain seven-bit text. URL `https://www.rfc-editor.org/rfc/rfcNNNN.html#section-N`.

- `MIME-Version: 1.0` is required. RFC 2045 sec. 4.
- `Content-Type` is `type/subtype` plus parameters; default `text/plain; charset=us-ascii`. RFC 2045 sec. 5.1, 5.2.
- `Content-Transfer-Encoding` is `7bit`, `8bit`, `binary`, `quoted-printable`, or `base64`; `7bit` is the default. RFC 2045 sec. 6.1, 6.2.
- Quoted-printable lines are at most 76 characters; `=XX` encodes a byte; a trailing `=` is a soft line break. RFC 2045 sec. 6.7.
- A multipart boundary is at most 70 characters, appears alone on a line as `--boundary`, and closes as `--boundary--`. RFC 2046 sec. 5.1.1.
- In `multipart/alternative` the plainest part comes first and readers show the last part they can render, so `text/plain` precedes `text/html`. RFC 2046 sec. 5.1.4.
- Non-ASCII text in `Subject` or a display name uses an encoded-word `=?charset?Q?text?=` or `?B?`, at most 75 characters each, never inside an address. RFC 2047 sec. 2, 4, 5.
- `Content-Disposition: attachment; filename=...; size=...` marks a file part. RFC 2183 sec. 2.

Conventions: every body is `multipart/alternative` with exactly two parts, `text/plain; charset=utf-8` then `text/html; charset=utf-8`. Pure ASCII under 78 characters per line uses `7bit`; anything else `quoted-printable`. `8bit`, `binary`, and `base64` never appear, so every file is seven-bit clean and every domain in a body is visible to text search.

```
Subject: =?UTF-8?Q?Factura_n=C2=BA_4471_pendiente?=
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="=_swk_5b2e91c7d0a3"

--=_swk_5b2e91c7d0a3
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

Adjunto la factura n=C2=BA 4471.
--=_swk_5b2e91c7d0a3
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<p>Adjunto la factura n=C2=BA 4471.</p>
--=_swk_5b2e91c7d0a3--
```

### External banner

The gateway inserts a one-line banner into every message it stamps with `X-Sentrywick-External: yes`, and into no internal message. In the `text/plain` part the first line is exactly

```
[External message. Sentrywick Gateway]
```

followed by one empty line and then the author's text. In the `text/html` part the generator emits this snippet verbatim, on one source line before any transfer encoding, immediately after the `<body ...>` tag, or as the first line when the part has no `<body>` tag:

```
<p style="margin:0;padding:6px 12px;background-color:#fff4d6;font-size:12px;color:#5a4a00;">[External message. Sentrywick Gateway]</p>
```

One product stamps one snippet, so the markup never varies between files and nothing is ever folded inside the banner. The snippet is longer than 78 characters, so under the convention above the HTML part of every external message is quoted-printable; the soft line breaks that encoding inserts decode away, and the decoded part carries the snippet on one line. Attacker text that imitates the banner is ordinary body text: it sits inside the author's part of the message and never replaces or precedes the real banner. The extractor reads the header, never the banner; the banner exists so an imitation can be compared with the real thing, which only works when the real one is identical in every file.

### Stripped attachments

No file carries a MIME attachment part, and `Content-Disposition: attachment` never appears. The headers say the gateway removed the file: one header per removed file, in original order, plus a notice in both body parts.

Header name: `X-Sentrywick-Removed-Attachment`. Value grammar in RFC 5234 ABNF style; `quoted-string`, `token`, `type/subtype` as in RFC 2045 sec. 5.1:

```
removed = "filename=" quoted-string "; size=" 1*DIGIT
          "; sha256=" 64HEXDIG "; action=" action
          [ "; type=" type "/" subtype ] [ "; reason=" token ]
action  = "stripped" / "quarantined"
```

`sha256` is 64 lowercase hex digits, the 256-bit SHA-256 digest length (RFC 6234 sec. 1, https://www.rfc-editor.org/rfc/rfc6234.html#section-1), generated from the corpus seed, never computed from a file; the ground truth records it so week 4 tools can look it up.

```
X-Sentrywick-Removed-Attachment: filename="Invoice_4471.pdf.exe"; size=184320;
  sha256=9c1d3e7f0a2b4c6d8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c1d;
  action=stripped; type=application/octet-stream; reason=blocked-extension
```

Body notice, last paragraph of the plain part and last `<p>` of the HTML part:

```
[Sentrywick Gateway removed 1 attachment: Invoice_4471.pdf.exe (184,320 bytes).
Details are in the message headers.]
```

The `X-` prefix mirrors deployed gateway products; RFC 6648 sec. 3 (https://www.rfc-editor.org/rfc/rfc6648.html#section-3) discourages it only for new standard fields.

Why this is safe for endpoint protection: the files contain only text. There is no base64 blob to decode, no executable bytes, no macro, no archive, nothing a student could open by accident. The hashes were never computed from real files, so they match no threat-intelligence list. Canvas serves plain text and antivirus sees prose, while the agent still gets the filename, size, and hash an analyst reads from a quarantine log.

## 3. Authentication-Results (RFC 8601)

`Authentication-Results` is the header the receiving gateway writes with the outcome of SPF, DKIM, and DMARC. SPF (Sender Policy Framework) asks whether the sending server's IP address may send for the envelope sender's domain. DKIM (DomainKeys Identified Mail) is a signature over selected headers and the body, checked with a key in the signing domain's DNS. DMARC (Domain-based Message Authentication, Reporting, and Conformance) asks whether SPF or DKIM passed for a domain matching the `From` domain, and applies the owner's policy if not. The agent reads this header rather than repeating the checks, as an analyst does. Base URL `https://www.rfc-editor.org/rfc/rfc8601.html#section-N`.

- Grammar: `authserv-id [version] ; method=result [reason] ptype.property=value ...`, one method per `;` clause, or `; none`. Sec. 2.2.
- `authserv-id` is the receiving gateway's host name. Sec. 2.5.
- ptypes: `smtp`, `header`, `body`, `policy`. Sec. 2.3.
- DKIM results: `none`, `pass`, `fail`, `policy`, `neutral`, `temperror`, `permerror`. Sec. 2.7.1.
- SPF results: `none`, `neutral`, `pass`, `policy`, `fail`, `softfail`, `temperror`, `permerror`. Sec. 2.7.2.
- DMARC results: `pass`, `fail`, `none`, `temperror`, `permerror`; properties `header.from` and `policy.dmarc`. RFC 9989 sec. 9.1 and 9.2, https://www.rfc-editor.org/rfc/rfc9989.html#section-9.2 (obsoletes RFC 7489 sec. 11.2).
- The gateway adds the header at the top, above any trace field it prepends. Sec. 4.
- A border gateway deletes any incoming `Authentication-Results` claiming its own authserv-id. Sec. 5.

`bestguesspass` is absent from the IANA registry (checked 2026-09-03, https://www.iana.org/assignments/email-auth/email-auth.xhtml); some products emit it when no DMARC record exists but alignment would have passed. The corpus does not use it. Properties: SPF `smtp.mailfrom` (optionally `smtp.helo`); DKIM `header.d`, `header.s`, optionally `header.i`, `header.b`.

### Alignment

DMARC passes only when an authenticated domain aligns with the `From` domain: the DKIM `d=` domain or the SPF-checked `MAIL FROM` domain shares its organizational domain (relaxed) or equals it (strict). RFC 7489 sec. 3.1 (https://www.rfc-editor.org/rfc/rfc7489.html#section-3.1), restated in RFC 9989 sec. 4.4 (https://www.rfc-editor.org/rfc/rfc9989.html#section-4.4); pass rule sec. 5.3.5; policy values `none`, `quarantine`, `reject` sec. 4.7.

The lesson: an attacker who owns `kestrelbrook-secure.example` can publish SPF and DKIM for it and collect three passes. Authentication proves the mail came from the domain it names, not that the display name is honest.

### Realistic combinations

Display-name spoof from an attacker-owned domain, all pass; the lie is the name:

```
From: "Dana Okafor (CFO)" <d.okafor@kestrelbrook-secure.example>
Authentication-Results: mx.kestrelbrook.example;
  spf=pass smtp.mailfrom=kestrelbrook-secure.example;
  dkim=pass header.d=kestrelbrook-secure.example header.s=k1
    header.i=@kestrelbrook-secure.example;
  dmarc=pass header.from=kestrelbrook-secure.example policy.dmarc=none
```

Direct forgery of a `p=reject` domain, nothing aligned:

```
From: Kestrelbrook IT <helpdesk@kestrelbrook.example>
Authentication-Results: mx.kestrelbrook.example;
  spf=fail smtp.mailfrom=kestrelbrook.example;
  dkim=none;
  dmarc=fail header.from=kestrelbrook.example policy.dmarc=reject
```

Marketing sender, SPF on the provider's bounce domain, no signature, no DMARC record:

```
Authentication-Results: mx.kestrelbrook.example;
  spf=pass smtp.mailfrom=bounce.larchwind-mail.example;
  dkim=none;
  dmarc=none header.from=deals.corvidridge-outfitters.example
```

Compromised partner account: all pass, exactly as in Scenario B of section 7; the tell is content and behavior, not headers.

Combination rules: `dmarc=pass` needs an aligned `spf=pass` or `dkim=pass`. `dmarc=fail` with `policy.dmarc=reject` or `quarantine` needs that policy in the corpus domain table. `dmarc=none` means no record and carries no `policy.dmarc`. `spf=softfail` fits a record ending `~all`, `spf=neutral` `?all`, `spf=none` no record, `dkim=fail` mail changed in transit. `temperror` and `permerror` appear in at most two messages each.

## 4. Received-SPF (RFC 7208) and DKIM-Signature (RFC 6376)

SPF defines the section 3 result codes except `policy` (RFC 7208 sec. 2.6, https://www.rfc-editor.org/rfc/rfc7208.html#section-2.6). DMARC uses the `MAIL FROM` identity, not `HELO` (RFC 9989 sec. 4.4.2). `Received-SPF` carries a result, a comment, and the pairs `receiver`, `client-ip`, `envelope-from`, `helo`, `identity`, `mechanism` (RFC 7208 sec. 9.1, https://www.rfc-editor.org/rfc/rfc7208.html#section-9.1):

```
Received-SPF: pass (mx.kestrelbrook.example: domain of
  bounce-8813-4471-9c4e1b7a2d5f8036@bounce.larchwind-mail.example designates
  198.51.100.23 as permitted sender) receiver=mx.kestrelbrook.example;
  client-ip=198.51.100.23;
  envelope-from="bounce-8813-4471-9c4e1b7a2d5f8036@bounce.larchwind-mail.example";
  helo=o17.mta.larchwind-mail.example; identity=mailfrom;
  mechanism=ip4:198.51.100.0/24
```

DKIM tags (RFC 6376 sec. 3.5, https://www.rfc-editor.org/rfc/rfc6376.html#section-3.5): `v=1` required; `a=rsa-sha256` recommended; `c=` header/body canonicalization, default `simple/simple`, `relaxed/relaxed` most common; `d=` signing domain; `s=` selector, published at `s._domainkey.d` (sec. 3.6.2.1); `h=` signed headers, which must include `From`; `bh=` body hash, base64; `b=` signature, base64.

```
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;
  d=larchwind-mail.example; s=s2026a; t=1776175964;
  h=from:to:subject:date:message-id:mime-version:content-type:
   list-unsubscribe:list-unsubscribe-post;
  bh=Qm9keSBoYXNoIGlzIHN5bnRoZXRpYyBhbmQgbm90IHJlYWw=;
  b=U2lnbmF0dXJlIGJ5dGVzIGFyZSBzeW50aGV0aWMuIFRoZXkgZG8gbm90IHZlcmlmeS4gVGhl
   IGNvdXJzZSByZWFkcyB0aGUgZ2F0ZXdheSB2ZXJkaWN0LCBub3QgdGhlIHNpZ25hdHVyZS4gU
   ...
```

`bh` is 44 base64 characters (32-byte SHA-256) and `b` is 344 (2048-bit RSA), both generated from the seed; neither verifies. That is acceptable because no lab verifies signatures: verification needs the signer's DNS key, which cannot exist under `.example`, and the course teaches the analyst's workflow of reading the gateway's `Authentication-Results` verdict (RFC 9989 sec. 5.3.6 asks receivers to write it).

## 5. ARC (RFC 8617)

ARC (Authenticated Received Chain) lets a forwarder or list record the authentication results it saw before modifying a message, in three headers per hop (`ARC-Authentication-Results`, `ARC-Message-Signature`, `ARC-Seal`) sharing an `i=` instance number (RFC 8617 sec. 4, https://www.rfc-editor.org/rfc/rfc8617.html#section-4). Recommendation: leave ARC out. The corpus has no list or forwarding hop, the labs never read ARC, and synthetic seals add unverifiable bulk. If the design adds a forwarded-from-webmail case, that message alone carries one ARC set with `i=1` and `cv=none` (sec. 4.1.3).

## 6. Reserved names and addresses

- `.test`, `.example`, `.invalid`, `.localhost` are reserved; `.example` is for documentation. RFC 2606 sec. 2, https://www.rfc-editor.org/rfc/rfc2606.html#section-2.
- `example.com`, `example.net`, `example.org` are reserved but resolvers treat them normally, and they resolve to a real host. RFC 2606 sec. 3; RFC 6761 sec. 6.5, https://www.rfc-editor.org/rfc/rfc6761.html#section-6.5.
- IPv4 documentation blocks `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, not routed. RFC 5737 sec. 3, https://www.rfc-editor.org/rfc/rfc5737.html#section-3.
- IPv6 documentation prefix `2001:db8::/32`. RFC 3849 sec. 2, https://www.rfc-editor.org/rfc/rfc3849.html#section-2.
- Private IPv4 `10/8`, `172.16/12`, `192.168/16`, not routed between organizations. RFC 1918 sec. 3, https://www.rfc-editor.org/rfc/rfc1918.html#section-3.

Domain policy: every domain in every header, body, and URL ends in `.example`, covering the organization, partners, attacker infrastructure, webmail and bulk-mail providers, and link hosts. Nothing resolves (the root zone has no `.example` delegation), nothing carries reputation, and no trademark is used, since no `.example` name can be registered. `example.com` and its siblings are excluded because they resolve; `.test`, `.invalid`, `.localhost` are excluded so the verifier needs one rule.

Lookalikes remain expressible: character swap (`kestre1brook.example`), transposition (`kestrelbrok.example`), added word (`kestrelbrook-secure.example`), subdomain trick (`kestrelbrook.example.account-services-portal.example`, the real name as a mere label). Internal hops use `10.20.0.0/16`; external hosts use the RFC 5737 blocks; IPv6 only from `2001:db8::/32`.

## 7. Received chains

Each accepting server prepends one `Received` line: `from` (the client's EHLO name, then its reverse name and address literal in parentheses), `by`, optional `with`, `id`, `for`, `;`, and a date-time with numeric offset (RFC 5321 sec. 4.4, https://www.rfc-editor.org/rfc/rfc5321.html#section-4.4). `with` keywords `ESMTPS` (TLS), `ESMTPSA` (TLS plus authentication), and `LMTP` come from RFC 3848 sec. 1 (https://www.rfc-editor.org/rfc/rfc3848.html#section-1). Top down, timestamps never increase; each `from` names the `by` of the line below; `Date` is at or just before the bottom hop.

### One mailbox, one store

The top `Received` line is the LMTP hop that hands the message to the mailbox store. A mailbox lives on exactly one store, so that hop is a property of the recipient and never of the path the message arrived on: internal mail and gateway mail for the same person land on the same host. The corpus records the store per mailbox in the `mailstore` field of `corpus/data/recipients.json`, generators read it from there, `corpus/tools/check_spec.py` fails when one recipient appears with two stores, and the verifier in section 10 checks the rendered files. Scenario A and Scenario B below deliver the same recipient by the same store for that reason. An analyst who pulls one mailbox out of the store and finds it living on two servers stops trusting the whole chain.

Scenario A, internal to internal, two hops:

```
Return-Path: <d.okafor@kestrelbrook.example>
Received: from mail.kestrelbrook.example (mail.kestrelbrook.example [10.20.4.25])
  by mailstore-02.kestrelbrook.example (Sentrywick Store 4.2) with LMTP
  id 3f9c2b7a-1d4e-4b0a-9c11-58e2a7d3f601
  for <m.reyes@kestrelbrook.example>; Tue, 14 Apr 2026 09:12:43 -0500
Received: from WKST-4471.corp.kestrelbrook.example ([10.20.31.144])
  by mail.kestrelbrook.example (Sentrywick Gateway 7.4) with ESMTPSA
  id 5a8e0c1d2f3b; Tue, 14 Apr 2026 09:12:42 -0500
Date: Tue, 14 Apr 2026 09:12:41 -0500
```

Scenario B, external sender through the gateway, three hops (the sender stamps in UTC, which is 09:12:44 local):

```
Return-Path: <ana.lindqvist@halvorsen-supply.example>
Received: from mx.kestrelbrook.example (mx.kestrelbrook.example [10.20.4.10])
  by mailstore-02.kestrelbrook.example (Sentrywick Store 4.2) with LMTP
  id 8c2d4e6f-7a90-4b1c-8d2e-3f4a5b6c7d8e
  for <m.reyes@kestrelbrook.example>; Tue, 14 Apr 2026 09:12:49 -0500
Authentication-Results: mx.kestrelbrook.example;
  spf=pass smtp.mailfrom=halvorsen-supply.example;
  dkim=pass header.d=halvorsen-supply.example header.s=mail2026;
  dmarc=pass header.from=halvorsen-supply.example policy.dmarc=quarantine
Received-SPF: pass (mx.kestrelbrook.example: domain of
  ana.lindqvist@halvorsen-supply.example designates 203.0.113.57 as
  permitted sender) receiver=mx.kestrelbrook.example;
  client-ip=203.0.113.57; envelope-from="ana.lindqvist@halvorsen-supply.example";
  helo=smtp-out.halvorsen-supply.example; identity=mailfrom; mechanism=mx
X-Sentrywick-Scan-Result: clean
Received: from smtp-out.halvorsen-supply.example
  (smtp-out.halvorsen-supply.example [203.0.113.57])
  by mx.kestrelbrook.example (Sentrywick Gateway 7.4) with ESMTPS
  (TLS1_3 TLS_AES_256_GCM_SHA384) id 9b1f7e3c5d2a;
  Tue, 14 Apr 2026 09:12:47 -0500
Received: from HSUP-LT-0219.halvorsen-supply.example ([192.0.2.14])
  by smtp-out.halvorsen-supply.example with ESMTPSA id 4d7a1c9e;
  Tue, 14 Apr 2026 14:12:44 +0000
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=halvorsen-supply.example;
  s=mail2026; h=from:to:subject:date:message-id; bh=...; b=...
Date: Tue, 14 Apr 2026 09:12:40 -0500
```

Scenario C, bulk-mail provider: the same three hops, the provider's bounce address as envelope sender, `Authentication-Results` as in Scenario B with `dmarc=none`, plus list headers. `List-Unsubscribe` holds comma-separated URLs in angle brackets (RFC 2369 sec. 3.2, https://www.rfc-editor.org/rfc/rfc2369.html#section-3.2). `List-Unsubscribe-Post: List-Unsubscribe=One-Click` requires an HTTPS URL and DKIM coverage of both headers (RFC 8058 sec. 3.1, https://www.rfc-editor.org/rfc/rfc8058.html#section-3.1). `List-Id` is an optional phrase and a bracketed dotted identifier (RFC 2919 sec. 3, https://www.rfc-editor.org/rfc/rfc2919.html#section-3). `Precedence: bulk` is a non-standard but widespread convention (RFC 3834 sec. 3.1.8, https://www.rfc-editor.org/rfc/rfc3834.html#section-3.1.8). `Feedback-ID` is an unstandardized optional field (RFC 5322 sec. 3.6.8) carrying campaign identifiers. The bounce address, the unsubscribe URL and every tracking link end in one opaque per-recipient token, because the one-click POST carries nothing that identifies the subscriber and the URI must (RFC 8058 sec. 3.1); the token is derived from the corpus seed. The provider's node stamps `Date` in UTC, as it does its own `Received` line and `Message-ID`, so the two header lines that carry the unbreakable bounce address may run a few characters past the 78-character recommendation while staying far under the 998 limit.

```
Return-Path: <bounce-8813-4471-9c4e1b7a2d5f8036@bounce.larchwind-mail.example>
Received: from mx.kestrelbrook.example ... with LMTP ...;
  Tue, 14 Apr 2026 06:30:12 -0500
Received: from o17.mta.larchwind-mail.example
  (o17.mta.larchwind-mail.example [198.51.100.23])
  by mx.kestrelbrook.example (Sentrywick Gateway 7.4) with ESMTPS
  id 2c4e6a8b0d1f; Tue, 14 Apr 2026 06:30:10 -0500
Received: from app-node-03.larchwind-mail.example ([192.0.2.140])
  by o17.mta.larchwind-mail.example with ESMTP id 71b3;
  Tue, 14 Apr 2026 11:30:04 +0000
From: Corvid Ridge Outfitters <deals@deals.corvidridge-outfitters.example>
List-Unsubscribe:
  <https://links.larchwind-mail.example/u/8813/4471/9c4e1b7a2d5f8036>,
  <mailto:unsub-8813-4471-9c4e1b7a2d5f8036@bounce.larchwind-mail.example>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
List-Id: Corvid Ridge Outfitters Deals <deals.corvidridge-outfitters.example>
Precedence: bulk
Feedback-ID: 8813:spring-clearance:corvidridge:larchwind
Date: Tue, 14 Apr 2026 11:29:58 +0000
```

## 8. Header ordering

From the top of a delivered external message: `Return-Path`, prepended once by the mailbox store at final delivery (RFC 5321 sec. 4.4); the store's `Received`; the gateway's block, `Authentication-Results` first, above its other trace fields (RFC 8601 sec. 4), then `Received-SPF`, the `X-Sentrywick-*` fields, and the gateway's `Received`; then the sender's `Received` lines, `DKIM-Signature`, and the author's client headers in the client's order. Nothing below the gateway's block is ever reordered (RFC 5322 sec. 3.6.7). Internal mail has no `Authentication-Results`, `Received-SPF`, or `DKIM-Signature`, since the gateway does not authenticate its own submissions; it still writes `X-Sentrywick-Scan-Result`.

## 9. Realism headers without a real vendor

All are optional fields under RFC 5322 sec. 3.6.8 unless cited.

- `X-Originating-IP: [203.0.113.88]`: a webmail provider records the user's client address.
- `X-Mailer: Marrowdale Mail 5.2`: fictional client names only.
- `X-Priority: 1` with `Importance: high`: urgency pressure; `Importance` values high, normal, low (RFC 4021 sec. 2.1.52, https://www.rfc-editor.org/rfc/rfc4021.html#section-2.1.52).
- `Thread-Topic: Vendor payment run for 4/17`: subject without `Re:`. House rule, since deployed products write this header and a quote header in one recognizable pair: in this corpus `Thread-Topic` belongs to the organization's submission host, which stamps it on the threaded mail it accepts from internal clients, so it marks the internal submission path and appears on no message that arrived through the gateway. The quoting form belongs to the client, and every client in the corpus uses one form, whatever host it submits through: an attribution line `On Mon, 13 Apr 2026 at 10:12, Accounts Payable wrote:`, then the quoted text one level deeper, `>` per level in the `text/plain` part and one nested `<blockquote>` per level in the `text/html` part. The block form (`From` / `Sent` / `To` / `Subject`) never appears. The attribution line for a nested message sits at the level of the message that quotes it, not at the level of the message it names, and the two body parts carry the same words at the same depth.
- `Auto-Submitted: auto-generated` for system notices, `auto-replied` for out-of-office (RFC 3834 sec. 5, https://www.rfc-editor.org/rfc/rfc3834.html#section-5).
- `X-Sentrywick-Scan-Result: clean | suspect | released-from-quarantine`: gateway verdict.
- `X-Sentrywick-Spam-Score: 6.8`: decimal 0.0 to 10.0.
- `X-Sentrywick-Message-UID: 9b1f7e3c5d2a`: matches the gateway `Received` id.
- `X-Sentrywick-Removed-Attachment`: section 2.
- `X-Sentrywick-Reported-By: m.reyes@kestrelbrook.example`: set when an employee reported the message; feeds week 4 `lookup_recipient`.

## 10. Verifier checklist

Run against every `.eml`; a failing file does not ship.

1. Every line ends with CRLF, no bare CR or LF, no line over 998 bytes before CRLF (RFC 5322 sec. 2.1, 2.1.1).
2. `email.message_from_bytes(data, policy=email.policy.default)` succeeds; `msg.defects` and every part's `.defects` are empty.
3. `Date` parses with `email.utils.parsedate_to_datetime`, has a numeric offset, and any day-of-week matches the date (RFC 5322 sec. 3.3).
4. `From`, `Date`, `Message-ID` appear exactly once; `Message-ID` matches `^<[A-Za-z0-9._+-]+@[a-z0-9.-]+\.example>$` (RFC 5322 sec. 3.6, 3.6.4).
5. If `In-Reply-To` is present, `References` is present and its last id equals it (RFC 5322 sec. 3.6.4).
6. `Return-Path` is the first header, appears once, and its domain ends in `.example` (RFC 5321 sec. 4.4).
7. At least one `Received`; the text after each line's last `;` parses as a datetime; top to bottom is non-increasing in UTC; each `from` host equals the `by` host below it; `Date` is at most 120 seconds after the bottom timestamp (RFC 5321 sec. 4.4; RFC 5322 sec. 3.6.7).
8. External messages: exactly one `Authentication-Results` that, unfolded, matches `^mx\.[a-z0-9.-]+\.example;(\s*(spf|dkim|dmarc)=(none|pass|fail|softfail|neutral|policy|temperror|permerror)(\s+[a-z]+\.[a-z]+=\S+)*;?)+$` and satisfies the combination rules in section 3 (RFC 8601 sec. 2.2, 2.7). Internal messages: none.
9. Every domain position ends in `.example`: the part after `@` in every address, `envelope-from`, `smtp.mailfrom`, `Return-Path`, and `for`; `Received` `from` and `by` names; `Message-ID` right side; `header.d`, `header.from`, `receiver`, `helo`; the `List-Id` namespace; the host of every `http`, `https`, or `mailto` URL in either body. Safety net: any token matching `\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\b` in the lowercased file, other than attachment filenames, fails if its last label is a delegated TLD in the IANA root zone list (https://data.iana.org/TLD/tlds-alpha-by-domain.txt); `example` is not delegated (RFC 2606 sec. 2, RFC 6761 sec. 6.5).
10. Every IPv4 literal is inside `10/8`, `172.16/12`, `192.168/16`, `192.0.2/24`, `198.51.100/24`, or `203.0.113/24`; every IPv6 literal starts with `2001:db8:` (RFC 1918 sec. 3, RFC 5737 sec. 3, RFC 3849 sec. 2).
11. `msg.get_content_type()` is `multipart/alternative`; the parts are exactly `text/plain` then `text/html`; no part has `Content-Disposition: attachment`; `list(msg.iter_attachments())` is empty (RFC 2046 sec. 5.1.4; RFC 2183 sec. 2.2).
12. Every `Content-Transfer-Encoding` is `7bit` or `quoted-printable`; the file contains only bytes 0x20 to 0x7E plus CR, LF, TAB (RFC 2045 sec. 6.1).
13. Every `X-Sentrywick-Removed-Attachment` matches the section 2 grammar with a 64-hex-digit `sha256`, and both body parts carry the notice naming the same filename.
14. If `DKIM-Signature` is present, tags `v=1`, `a=`, `c=`, `d=`, `s=`, `h=` (containing `from`), `bh=` (44 base64 chars), `b=` are present and `d=` ends in `.example` (RFC 6376 sec. 3.5).
15. No `ARC-*` header unless the ground truth flags the message as a forwarding case (section 5).
16. No `Authentication-Results` names an authserv-id other than the organization's gateway (RFC 8601 sec. 5).
17. Messages carrying `X-Sentrywick-External: yes`: the decoded `text/plain` part begins with the line `[External message. Sentrywick Gateway]` followed by an empty line, and the decoded `text/html` part contains the section 2 banner snippet byte for byte on one line, as its first line or immediately after the `<body ...>` tag; the string `[External message. Sentrywick Gateway]` occurs exactly once in each decoded part. Messages without that header: the string occurs in neither part (section 2).
18. The top `Received` line's LMTP hop delivers by the store that `data/recipients.json` gives the address in its `for` clause, so no mailbox appears on two stores (section 7).
