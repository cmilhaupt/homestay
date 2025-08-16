# Homestay

Homestay is a self-hostable, customizable booking app for you or your friend's
properties. It's designed to be simple host, modify, or extend to your specific
needs. 

# Features
* PIN-based login
* Rate-limiting on all endpoints
* Availability display only for bookees
* Full booking details for admins
* Separate login pages for booking and administering bookings
* Email notifications for admins and bookees
* Simple SQLite backend storage

# Building
```bash
docker compose build
docker up -d
```
Starts a server at localhost:8080 by default.

# Responsible LLM Use Disclosure
This repository contains content generated or assisted by Large Language Models
(LLMs). While LLMs can be powerful tools for augmenting human capabilities, they
are not a replacement for critical thinking and intellectual rigor. The author
of this document has made efforts to ensure that any LLM-generated content is
accurately attributed and transparently disclosed. However, readers should be
aware the LLMs may introduce subtle biases, errors, or limitations that are not
immediately apparent.

To maintain the integrity and accountability of the work, the author commits to
the following principles:
* Training: efforts have been made to stay current with the latest developments
  and limitations of LLMs, and to use the judiciously and with careful
  consideration
* Transparency: we acknowledge the use of LLMs in this codebase and disclose any
  generated content
* Traceability: we make available, upon request, the prompts and inputs used to
  generate any LLM-assisted content

Readers are encouraged to critically evaluate the content of this document,
considering the potential risks and limitations associated with LLM-generated
material. 
