"""
Clay-like Data Enrichment and GTM Automation
Provides multi-source data enrichment, intent signals, and workflow automation
similar to Clay.com functionality
"""

import time
import re
import os
from typing import Dict, Optional, List, Any
from datetime import datetime
import json


class DataEnrichmentEngine:
    """
    Multi-source data enrichment engine similar to Clay.com
    Provides waterfall enrichment across multiple data sources
    """
    
    def __init__(self):
        self.enrichment_sources = []
        self.enrichment_history = []
    
    def add_enrichment_source(self, source_name: str, enrichment_func):
        """Add a data enrichment source."""
        self.enrichment_sources.append({
            'name': source_name,
            'function': enrichment_func
        })
    
    def waterfall_enrich(self, record: Dict[str, Any], fields_to_enrich: List[str]) -> Dict[str, Any]:
        """
        Waterfall enrichment: try multiple sources until all fields are found.
        Similar to Clay's multi-provider enrichment.
        """
        enriched_record = record.copy()
        missing_fields = [field for field in fields_to_enrich if not enriched_record.get(field)]
        
        for source in self.enrichment_sources:
            if not missing_fields:
                break
            
            try:
                print(f"  Trying {source['name']}...")
                result = source['function'](enriched_record)
                
                # Update only missing fields
                for field in missing_fields[:]:
                    if result.get(field) and not enriched_record.get(field):
                        enriched_record[field] = result[field]
                        missing_fields.remove(field)
                        print(f"    ✓ Found {field} via {source['name']}")
                
                self.enrichment_history.append({
                    'source': source['name'],
                    'timestamp': datetime.now().isoformat(),
                    'fields_found': [f for f in fields_to_enrich if result.get(f)]
                })
                
            except Exception as e:
                print(f"    ✗ Error with {source['name']}: {str(e)}")
                continue
        
        return enriched_record


class IntentSignalsTracker:
    """
    Track intent signals: job changes, news, social mentions, website visits
    Similar to Clay's Signals feature
    """
    
    def __init__(self):
        self.signals = []
    
    def track_job_change(self, person_name: str, old_company: str, new_company: str, 
                        new_title: str, date: str = None):
        """Track job changes as intent signals."""
        signal = {
            'type': 'job_change',
            'person': person_name,
            'old_company': old_company,
            'new_company': new_company,
            'new_title': new_title,
            'date': date or datetime.now().isoformat(),
            'intent_score': 85  # High intent - new job = buying opportunity
        }
        self.signals.append(signal)
        return signal
    
    def track_news_mention(self, company: str, headline: str, url: str, date: str = None):
        """Track news mentions as intent signals."""
        signal = {
            'type': 'news_mention',
            'company': company,
            'headline': headline,
            'url': url,
            'date': date or datetime.now().isoformat(),
            'intent_score': 60  # Medium intent
        }
        self.signals.append(signal)
        return signal
    
    def track_social_mention(self, company: str, platform: str, content: str, date: str = None):
        """Track social media mentions as intent signals."""
        signal = {
            'type': 'social_mention',
            'company': company,
            'platform': platform,
            'content': content,
            'date': date or datetime.now().isoformat(),
            'intent_score': 50  # Medium intent
        }
        self.signals.append(signal)
        return signal
    
    def track_website_visit(self, company: str, visitor_email: str, pages_visited: List[str], 
                           date: str = None):
        """Track website visits as intent signals."""
        signal = {
            'type': 'website_visit',
            'company': company,
            'visitor_email': visitor_email,
            'pages_visited': pages_visited,
            'date': date or datetime.now().isoformat(),
            'intent_score': 75  # High intent - active interest
        }
        self.signals.append(signal)
        return signal
    
    def get_signals_for_company(self, company_name: str) -> List[Dict]:
        """Get all intent signals for a specific company."""
        return [s for s in self.signals if s.get('company', '').lower() == company_name.lower()]
    
    def get_signals_for_person(self, person_name: str) -> List[Dict]:
        """Get all intent signals for a specific person."""
        return [s for s in self.signals if s.get('person', '').lower() == person_name.lower()]


class WorkflowAutomation:
    """
    Workflow automation engine similar to Clay's Sculptor
    Build GTM workflows with conditional logic
    """
    
    def __init__(self):
        self.workflows = []
    
    def create_workflow(self, name: str, steps: List[Dict[str, Any]]):
        """Create a new workflow with steps."""
        workflow = {
            'name': name,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'enabled': True
        }
        self.workflows.append(workflow)
        return workflow
    
    def add_conditional_step(self, condition: str, action_if_true: Dict, action_if_false: Dict = None):
        """
        Add conditional logic step.
        Example: enrich only if email is missing, use different provider if company size > 100
        """
        return {
            'type': 'conditional',
            'condition': condition,
            'if_true': action_if_true,
            'if_false': action_if_false
        }
    
    def add_enrichment_step(self, fields: List[str], providers: List[str] = None):
        """Add data enrichment step to workflow."""
        return {
            'type': 'enrichment',
            'fields': fields,
            'providers': providers or ['default']
        }
    
    def add_action_step(self, action_type: str, destination: str, data: Dict = None):
        """Add action step (update CRM, send email, etc.)."""
        return {
            'type': 'action',
            'action_type': action_type,
            'destination': destination,
            'data': data or {}
        }
    
    def execute_workflow(self, workflow_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow on a record."""
        workflow = next((w for w in self.workflows if w['name'] == workflow_name and w['enabled']), None)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found or disabled")
        
        result = record.copy()
        
        for step in workflow['steps']:
            if step['type'] == 'conditional':
                # Evaluate condition (simplified - would need proper expression evaluator)
                condition_met = self._evaluate_condition(step['condition'], result)
                if condition_met:
                    result = self._execute_action(step['if_true'], result)
                elif step.get('if_false'):
                    result = self._execute_action(step['if_false'], result)
            
            elif step['type'] == 'enrichment':
                # Perform enrichment
                fields = step.get('fields', [])
                for field in fields:
                    if not result.get(field):
                        # Try to enrich (would call actual enrichment function)
                        pass
            
            elif step['type'] == 'action':
                # Execute action
                result = self._execute_action(step, result)
        
        return result
    
    def _evaluate_condition(self, condition: str, record: Dict) -> bool:
        """Evaluate a condition string against a record."""
        # Simplified condition evaluator
        # In production, would use a proper expression parser
        try:
            # Example: "email == None" or "company_size > 100"
            if '==' in condition:
                parts = condition.split('==')
                field = parts[0].strip()
                value = parts[1].strip().strip('"\'')
                return str(record.get(field, '')) == value
            elif '>' in condition:
                parts = condition.split('>')
                field = parts[0].strip()
                value = int(parts[1].strip())
                return int(record.get(field, 0)) > value
            elif '<' in condition:
                parts = condition.split('<')
                field = parts[0].strip()
                value = int(parts[1].strip())
                return int(record.get(field, 0)) < value
            return False
        except:
            return False
    
    def _execute_action(self, action: Dict, record: Dict) -> Dict:
        """Execute an action on a record."""
        # Placeholder - would integrate with actual systems
        return record


class AudienceBuilder:
    """
    Build dynamic audiences by combining signals, enrichment, and CRM data
    Similar to Clay's Audiences feature
    """
    
    def __init__(self):
        self.audiences = []
    
    def create_audience(self, name: str, criteria: Dict[str, Any]) -> Dict:
        """Create a new audience with criteria."""
        audience = {
            'name': name,
            'criteria': criteria,
            'created_at': datetime.now().isoformat(),
            'records': []
        }
        self.audiences.append(audience)
        return audience
    
    def add_criteria(self, audience_name: str, field: str, operator: str, value: Any):
        """Add criteria to an audience."""
        audience = next((a for a in self.audiences if a['name'] == audience_name), None)
        if audience:
            if 'criteria' not in audience:
                audience['criteria'] = {}
            audience['criteria'][field] = {
                'operator': operator,
                'value': value
            }
    
    def match_records(self, audience_name: str, records: List[Dict]) -> List[Dict]:
        """Match records against audience criteria."""
        audience = next((a for a in self.audiences if a['name'] == audience_name), None)
        if not audience:
            return []
        
        matched = []
        for record in records:
            if self._matches_criteria(record, audience['criteria']):
                matched.append(record)
        
        audience['records'] = matched
        audience['last_updated'] = datetime.now().isoformat()
        return matched
    
    def _matches_criteria(self, record: Dict, criteria: Dict) -> bool:
        """Check if a record matches audience criteria."""
        for field, condition in criteria.items():
            record_value = record.get(field)
            operator = condition.get('operator')
            value = condition.get('value')
            
            if operator == 'equals':
                if str(record_value) != str(value):
                    return False
            elif operator == 'contains':
                if value not in str(record_value):
                    return False
            elif operator == 'greater_than':
                if float(record_value or 0) <= float(value):
                    return False
            elif operator == 'less_than':
                if float(record_value or 0) >= float(value):
                    return False
            elif operator == 'is_empty':
                if record_value:
                    return False
            elif operator == 'is_not_empty':
                if not record_value:
                    return False
        
        return True


class CRMIntegration:
    """
    CRM integration for syncing enriched data
    Supports Salesforce, HubSpot, and other CRMs
    """
    
    def __init__(self):
        self.integrations = {}
    
    def connect_crm(self, crm_type: str, credentials: Dict):
        """Connect to a CRM."""
        self.integrations[crm_type] = {
            'type': crm_type,
            'credentials': credentials,
            'connected_at': datetime.now().isoformat(),
            'connected': True
        }
        return True
    
    def sync_record(self, crm_type: str, record: Dict, operation: str = 'upsert'):
        """Sync a record to CRM."""
        if crm_type not in self.integrations:
            raise ValueError(f"CRM {crm_type} not connected")
        
        # Placeholder - would use actual CRM APIs
        print(f"  Syncing to {crm_type}: {operation} - {record.get('name', 'Unknown')}")
        return {
            'success': True,
            'crm_id': f"{crm_type}_12345",
            'operation': operation
        }
    
    def bulk_sync(self, crm_type: str, records: List[Dict], operation: str = 'upsert'):
        """Bulk sync records to CRM."""
        results = []
        for record in records:
            try:
                result = self.sync_record(crm_type, record, operation)
                results.append(result)
            except Exception as e:
                results.append({'success': False, 'error': str(e)})
        return results


class EmailSequencer:
    """
    Automated email sequence automation
    Similar to Clay's Sequencer feature
    """
    
    def __init__(self):
        self.sequences = []
        self.sent_emails = []
    
    def create_sequence(self, name: str, steps: List[Dict]) -> Dict:
        """Create an email sequence."""
        sequence = {
            'name': name,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
            'enabled': True
        }
        self.sequences.append(sequence)
        return sequence
    
    def add_email_step(self, subject: str, body_template: str, delay_days: int = 0, 
                      conditions: Dict = None) -> Dict:
        """Add an email step to sequence."""
        return {
            'type': 'email',
            'subject': subject,
            'body_template': body_template,
            'delay_days': delay_days,
            'conditions': conditions or {}
        }
    
    def add_wait_step(self, days: int) -> Dict:
        """Add a wait step to sequence."""
        return {
            'type': 'wait',
            'days': days
        }
    
    def send_sequence(self, sequence_name: str, recipient: Dict):
        """Send an email sequence to a recipient."""
        sequence = next((s for s in self.sequences if s['name'] == sequence_name and s['enabled']), None)
        if not sequence:
            raise ValueError(f"Sequence '{sequence_name}' not found or disabled")
        
        # Placeholder - would integrate with email service
        print(f"  Starting sequence '{sequence_name}' for {recipient.get('email')}")
        
        for step in sequence['steps']:
            if step['type'] == 'email':
                # Personalize email
                subject = self._personalize_template(step['subject'], recipient)
                body = self._personalize_template(step['body_template'], recipient)
                
                # Send email (placeholder)
                email_record = {
                    'sequence': sequence_name,
                    'recipient': recipient.get('email'),
                    'subject': subject,
                    'body': body,
                    'sent_at': datetime.now().isoformat()
                }
                self.sent_emails.append(email_record)
                print(f"    ✓ Sent: {subject}")
                
                # Wait before next step
                if step.get('delay_days', 0) > 0:
                    print(f"    ⏳ Waiting {step['delay_days']} days...")
            
            elif step['type'] == 'wait':
                print(f"    ⏳ Waiting {step['days']} days...")
        
        return self.sent_emails
    
    def _personalize_template(self, template: str, recipient: Dict) -> str:
        """Personalize email template with recipient data."""
        result = template
        for key, value in recipient.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result


class ClayLikePlatform:
    """
    Main platform class that combines all Clay-like features
    """
    
    def __init__(self):
        self.enrichment_engine = DataEnrichmentEngine()
        self.signals_tracker = IntentSignalsTracker()
        self.workflow_automation = WorkflowAutomation()
        self.audience_builder = AudienceBuilder()
        self.crm_integration = CRMIntegration()
        self.email_sequencer = EmailSequencer()
    
    def enrich_record(self, record: Dict, fields: List[str]) -> Dict:
        """Enrich a record using waterfall enrichment."""
        return self.enrichment_engine.waterfall_enrich(record, fields)
    
    def track_signal(self, signal_type: str, **kwargs):
        """Track an intent signal."""
        if signal_type == 'job_change':
            return self.signals_tracker.track_job_change(**kwargs)
        elif signal_type == 'news':
            return self.signals_tracker.track_news_mention(**kwargs)
        elif signal_type == 'social':
            return self.signals_tracker.track_social_mention(**kwargs)
        elif signal_type == 'website_visit':
            return self.signals_tracker.track_website_visit(**kwargs)
    
    def create_workflow(self, name: str, steps: List[Dict]):
        """Create a GTM workflow."""
        return self.workflow_automation.create_workflow(name, steps)
    
    def execute_workflow(self, workflow_name: str, record: Dict) -> Dict:
        """Execute a workflow on a record."""
        return self.workflow_automation.execute_workflow(workflow_name, record)
    
    def build_audience(self, name: str, criteria: Dict) -> Dict:
        """Build a dynamic audience."""
        return self.audience_builder.create_audience(name, criteria)
    
    def sync_to_crm(self, crm_type: str, records: List[Dict]):
        """Sync records to CRM."""
        return self.crm_integration.bulk_sync(crm_type, records)
    
    def create_email_sequence(self, name: str, steps: List[Dict]):
        """Create an email sequence."""
        return self.email_sequencer.create_sequence(name, steps)
    
    def send_email_sequence(self, sequence_name: str, recipient: Dict):
        """Send an email sequence."""
        return self.email_sequencer.send_sequence(sequence_name, recipient)


# Example usage functions
def create_enrichment_workflow():
    """Example: Create a workflow for enriching leads."""
    platform = ClayLikePlatform()
    
    # Create workflow
    workflow = platform.create_workflow("Lead Enrichment", [
        platform.workflow_automation.add_conditional_step(
            condition="email == None",
            action_if_true=platform.workflow_automation.add_enrichment_step(['email', 'phone']),
            action_if_false=platform.workflow_automation.add_enrichment_step(['phone'])
        ),
        platform.workflow_automation.add_action_step(
            action_type='sync_crm',
            destination='salesforce',
            data={'operation': 'upsert'}
        )
    ])
    
    return workflow


def create_outbound_sequence():
    """Example: Create an outbound email sequence."""
    platform = ClayLikePlatform()
    
    sequence = platform.create_email_sequence("Cold Outreach", [
        platform.email_sequencer.add_email_step(
            subject="Quick question about {{company}}",
            body_template="Hi {{name}},\n\nI noticed {{company}}...",
            delay_days=0
        ),
        platform.email_sequencer.add_wait_step(3),
        platform.email_sequencer.add_email_step(
            subject="Following up",
            body_template="Hi {{name}},\n\nJust following up...",
            delay_days=0
        )
    ])
    
    return sequence

