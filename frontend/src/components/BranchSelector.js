import React from 'react';
import { useBranch } from '../context/BranchContext';
import { useAuth } from '../context/AuthContext';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Building2 } from 'lucide-react';

export default function BranchSelector({ className = '', showLabel = false }) {
  const { user, hasRole } = useAuth();
  const { 
    branches, 
    selectedBranchId, 
    selectBranch, 
    canSelectAllBranches,
    loading 
  } = useBranch();

  // الموظفون المقيدون بفرع لا يمكنهم تغيير الفرع
  const isRestricted = user?.branch_id && !hasRole(['admin', 'super_admin', 'manager']);

  if (loading || branches.length === 0) {
    return null;
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {showLabel && (
        <Building2 className="h-4 w-4 text-muted-foreground" />
      )}
      <Select 
        value={selectedBranchId} 
        onValueChange={selectBranch}
        disabled={isRestricted}
      >
        <SelectTrigger 
          className="w-[160px] h-9 bg-card/50 border-border/50 text-sm"
          data-testid="branch-selector"
        >
          <SelectValue placeholder="اختر الفرع" />
        </SelectTrigger>
        <SelectContent>
          {canSelectAllBranches() && (
            <SelectItem value="all" data-testid="branch-option-all">
              جميع الفروع
            </SelectItem>
          )}
          {branches.map(branch => (
            <SelectItem 
              key={branch.id} 
              value={branch.id}
              data-testid={`branch-option-${branch.id}`}
            >
              {branch.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
