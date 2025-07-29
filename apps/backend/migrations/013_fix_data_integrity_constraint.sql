-- Fix the affected_system_property constraint to use data_integrity instead of transaction_integrity

-- Drop the existing constraint
ALTER TABLE step1_hazards 
DROP CONSTRAINT IF EXISTS step1_hazards_affected_system_property_check;

-- Add the updated constraint with data_integrity
ALTER TABLE step1_hazards 
ADD CONSTRAINT step1_hazards_affected_system_property_check 
CHECK (affected_system_property IN (
    'data_integrity', 'data_protection', 'service_availability',
    'regulatory_compliance', 'operational_capability', 'mission_effectiveness'
));