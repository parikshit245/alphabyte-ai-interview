import { Role } from "@repo/shared-types";

export function hasPermission(userRole: Role, requiredRole: Role): boolean {
  const roleHierarchy: Record<Role, number> = {
    [Role.CANDIDATE]: 1,
    [Role.RECRUITER]: 2,
    [Role.ADMIN]: 3,
    [Role.SUPER_ADMIN]: 4,
  };

  return roleHierarchy[userRole] >= roleHierarchy[requiredRole];
}

export function canAccessResource(
  userRole: Role,
  userId: string,
  resourceOwnerId: string
): boolean {
  // Super admin and admin can access everything
  if (userRole === Role.SUPER_ADMIN || userRole === Role.ADMIN) {
    return true;
  }

  // Users can only access their own resources
  return userId === resourceOwnerId;
}
