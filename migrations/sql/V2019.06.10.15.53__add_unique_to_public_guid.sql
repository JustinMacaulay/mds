ALTER TABLE application ADD CONSTRAINT application_guid_unique UNIQUE (application_guid);
ALTER TABLE document_manager ADD CONSTRAINT document_guid_unique UNIQUE (application_guid);
ALTER TABLE mine_party_appt ADD CONSTRAINT mine_party_appt_guid_unique UNIQUE (mine_party_appt_guid);
ALTER TABLE permit_amendment_document ADD CONSTRAINT permit_amendment_document_guid_unique UNIQUE (permit_amendment_document_guid);