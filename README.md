# Cold Email Deliverability Toolkit

> Open-source cold email deliverability toolkit with domain warmup scheduling, suppression management, and CASL/CAN-SPAM compliance automation. Built by [Avalux](https://avalux.io) for B2B sales teams and agencies who need bulletproof email infrastructure.

## Why this exists

Cold email deliverability is a technical problem masquerading as a marketing problem. Most sales teams focus on subject lines and copy while their emails land in spam because of poor sender reputation, inadequate warmup protocols, and compliance gaps.

This toolkit addresses the infrastructure layer: systematic domain warmup schedules, automated suppression list management, real-time deliverability monitoring, and built-in CASL/CAN-SPAM compliance. It's the foundation you need before worrying about open rates.

The reality is that 67% of cold emails never reach the inbox due to deliverability issues, not content problems. Domain reputation takes 4-8 weeks to establish properly, and most teams rush the process or skip critical steps like gradual volume ramping and engagement simulation.

## Who this is for

**B2B Sales Teams** who send 500+ cold emails per month and need systematic deliverability management beyond basic ESP features.

**Digital Agencies** managing cold email campaigns for multiple clients, requiring white-label compliance tools and centralized suppression management.

**Sales Development Representatives** who need automated warmup protocols and real-time deliverability feedback without manual monitoring.

**Compliance Officers** at companies operating in Canada, EU, or other jurisdictions requiring CASL/GDPR-compliant suppression workflows.

This is **not** for basic email marketing, transactional emails, or teams sending less than 100 emails per week.

## What's in the box

```
cold-email-deliverability-toolkit/
├── src/
│   ├── warmup/
│   │   ├── scheduler.py          # Domain warmup scheduling engine
│   │   ├── volume_ramp.py        # Progressive volume increase logic
│   │   └── engagement_sim.py     # Automated engagement simulation
│   ├── suppression/
│   │   ├── list_manager.py       # Suppression list CRUD operations
│   │   ├── casl_handler.py       # CASL-specific suppression logic
│   │   └── sync_engine.py        # Multi-ESP suppression sync
│   ├── compliance/
│   │   ├── footer_generator.py   # Dynamic CASL/CAN-SPAM footers
│   │   ├── consent_tracker.py    # Consent and opt-out tracking
│   │   └── audit_logger.py       # Compliance audit trail
│   ├── monitoring/
│   │   ├── reputation_check.py   # Domain/IP reputation monitoring
│   │   ├── deliverability_test.py # Inbox placement testing
│   │   └── bounce_handler.py     # Bounce classification and handling
│   └── integrations/
│       ├── sendgrid_client.py    # SendGrid API integration
│       ├── mailgun_client.py     # Mailgun API integration
│       └── postmark_client.py    # Postmark API integration
├── config/
│   ├── warmup_schedules.json     # Predefined warmup templates
│   ├── compliance_templates.json # Footer and consent templates
│   └── reputation_thresholds.json # Alert thresholds and limits
├── tests/
│   ├── test_warmup.py
│   ├── test_suppression.py
│   └── test_compliance.py
├── docs/
│   ├── warmup_guide.md           # Domain warmup best practices
│   ├── compliance_guide.md       # CASL/CAN-SPAM implementation
│   └── api_reference.md          # Complete API documentation
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Quick start

```bash
# Clone the repository
git clone https://github.com/elikem2021/cold-email-deliverability-toolkit.git
cd cold-email-deliverability-toolkit

# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your ESP API keys and database credentials

# Initialize database
python src/setup_db.py

# Start warmup for new domain
python src/warmup/scheduler.py --domain "newdomain.com" --schedule "conservative"

# Add emails to suppression list
python src/suppression/list_manager.py --add "user@example.com" --reason "casl_opt_out"

# Generate CASL-compliant footer
python src/compliance/footer_generator.py --jurisdiction "canada" --company "Your Company"

# Check domain reputation
python src/monitoring/reputation_check.py --domain "yourdomain.com"
```

## Domain warmup scheduling

The warmup scheduler implements progressive volume ramping based on domain age, previous sending history, and target volume. Three predefined schedules handle different risk profiles:

**Conservative Schedule (New Domains)**
- Week 1: 10 emails/day, 2 emails/hour max
- Week 2: 25 emails/day, 5 emails/hour max
- Week 3: 50 emails/day, 8 emails/hour max
- Week 4: 100 emails/day, 15 emails/hour max
- Week 5+: Full volume with 25 emails/hour limit

**Moderate Schedule (Established Domains)**
- Week 1: 50 emails/day, 10 emails/hour max
- Week 2: 150 emails/day, 20 emails/hour max
- Week 3: 300 emails/day, 35 emails/hour max
- Week 4+: Full volume with 50 emails/hour limit

**Aggressive Schedule (Warmed Domains)**
- Week 1: 200 emails/day, 30 emails/hour max
- Week 2: 500 emails/day, 50 emails/hour max
- Week 3+: Full volume with 75 emails/hour limit

The scheduler automatically adjusts based on bounce rates, spam complaints, and reputation scores. If bounce rate exceeds 3% or spam complaints exceed 0.1%, sending pauses for 24 hours and resumes at 50% previous volume.

## Suppression list management

The suppression engine maintains separate lists for different opt-out types and automatically syncs across multiple ESPs. CASL compliance requires specific handling for Canadian recipients:

```python
# CASL-specific suppression categories
CASL_CATEGORIES = {
    'explicit_opt_out': 'User clicked unsubscribe link',
    'implied_consent_expired': 'Implied consent exceeded 2-year limit',
    'no_existing_relationship': 'No prior business relationship',
    'bounced_invalid': 'Email address invalid/non-existent'
}

# Automatic suppression triggers
AUTO_SUPPRESS_CONDITIONS = {
    'hard_bounce': True,
    'spam_complaint': True,
    'unsubscribe_request': True,
    'casl_opt_out': True,
    'multiple_soft_bounces': 3  # Suppress after 3 consecutive soft bounces
}
```

The system generates timestamped suppression records with reason codes for audit compliance and automatically removes suppressed emails from active campaigns within 60 seconds.

## Compliance automation

CASL and CAN-SPAM compliance is built into every outbound email through dynamic footer generation and consent tracking:

**CASL Footer Requirements (Canada)**
- Sender identification (name and contact info)
- Unsubscribe mechanism
- Physical mailing address
- Reason for contact (existing relationship or consent)

**CAN-SPAM Footer Requirements (USA)**
- Clear sender identification
- Physical postal address
- Opt-out instructions
- "Advertisement" label if applicable

Footers are generated dynamically based on recipient location, sender jurisdiction, and campaign type. The system tracks all consent interactions and maintains audit logs for regulatory compliance.

## Deliverability monitoring

Real-time monitoring tracks key deliverability metrics across all sending domains:

- **Sender Score**: Daily checks via Sender Score API
- **Blacklist Status**: Monitors 15+ major blacklists
- **Inbox Placement**: Weekly seed testing to major providers
- **Authentication Status**: SPF, DKIM, DMARC validation
- **Engagement Rates**: Open/click tracking with ISP feedback loops

Alerts trigger when reputation scores drop below configurable thresholds or blacklist appearances are detected. The system can automatically pause sending and initiate remediation workflows.

## ESP integrations

Pre-built integrations handle common ESP operations through official APIs:

**SendGrid Integration**
- Suppression list sync via Suppression Management API
- Bounce/spam complaint webhooks
- Reputation monitoring via Stats API
- Template management for compliance footers

**Mailgun Integration**
- Domain reputation tracking
- Suppression list management
- Bounce classification and handling
- Delivery analytics and reporting

**Postmark Integration**
- Bounce webhook processing
- Suppression list synchronization
- Delivery tracking and analytics
- Template-based footer injection

All integrations use official APIs with proper authentication and rate limiting. No web scraping or unofficial endpoints.

## Production considerations

This open-source toolkit provides the foundation for production cold email deliverability, but real-world deployment requires additional hardening:

**Database scaling** for high-volume suppression list operations and audit logging

**Redis caching** for real-time reputation checks and rate limiting

**Webhook security** with proper signature validation and replay protection

**Multi-tenant isolation** for agency environments with client separation

**Advanced monitoring** with custom alerting and escalation workflows

**Compliance reporting** with automated audit trail generation and export

The codebase includes TODO comments marking areas requiring production enhancement.

## Why we built this

At [Avalux](https://avalux.io), we've seen too many B2B sales teams struggle with email deliverability while focusing on the wrong metrics. Great copy doesn't matter if emails never reach the inbox.

Most existing solutions are either too basic (simple warmup tools) or too expensive (enterprise deliverability platforms). This toolkit bridges that gap with production-ready infrastructure that scales from startup sales teams to agency environments.

We're open-sourcing our core deliverability stack because better email infrastructure benefits the entire B2B sales ecosystem. When everyone follows proper warmup protocols and compliance standards, it improves deliverability for all legitimate senders.

Need help implementing this in your sales stack or want custom integrations for your specific ESP setup? [Contact Avalux](https://avalux.io) for implementation consulting and production hardening services.

## Avalux's other open source projects

- [Freight ETA Toolkit](https://github.com/elikem2021/freight-eta-toolkit) - Real-time shipment tracking with geofencing and ETA prediction
- [Cold Email Deliverability Toolkit](https://github.com/elikem2021/cold-email-deliverability-toolkit) - Domain warmup, suppression management, and compliance automation

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Keywords

cold email deliverability, email warmup open source, domain reputation management, CASL compliance automation, CAN-SPAM compliance, suppression list management, B2B email deliverability, cold email infrastructure, email compliance toolkit, sender reputation monitoring, bounce handling automation, spam complaint management, email authentication setup, deliverability monitoring tools, cold outreach compliance