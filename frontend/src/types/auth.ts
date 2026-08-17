export interface AuthTokens {
    access: string;
    refresh: string;
}

export interface SchoolMembership {
    public_id: string;
    student: string;
    school: string;
    curriculum_plan: string;
    verified_by: string | null;
    verified_at: string | null;
    is_active: boolean;
}

export interface SchoolDelegation {
    public_id: string;
    delegate: string;
    school: string;
    assigned_by: string | null;
    is_active: boolean;
    created_at: string;
}

export interface CurrentUser {
    public_id: string;
    email: string;
    full_name: string;
    picture_url: string;
    is_platform_admin: boolean;
    cui: string | null;
    school_memberships?: SchoolMembership[];
    delegations?: SchoolDelegation[];
}
