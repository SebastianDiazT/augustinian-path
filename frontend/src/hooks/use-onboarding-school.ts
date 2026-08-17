import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';

export interface Faculty {
    public_id: string;
    area: string;
    name: string;
}

export interface ProfessionalSchool {
    public_id: string;
    faculty: Faculty;
    name: string;
}

export interface CurriculumPlan {
    public_id: string;
    name: string;
}

interface MembershipRequestData {
    public_id: string;
    status: string;
}

export const ACADEMIC_AREAS = [
    { value: 'biomedicas', label: 'Biomédicas' },
    { value: 'ingenierias', label: 'Ingenierías' },
    { value: 'sociales', label: 'Sociales' },
];

export function useOnboardingSchool() {
    const [allFaculties, setAllFaculties] = useState<Faculty[]>([]);
    const [allSchools, setAllSchools] = useState<ProfessionalSchool[]>([]);
    const [plans, setPlans] = useState<CurriculumPlan[]>([]);

    const [selectedArea, setSelectedArea] = useState('');
    const [selectedFaculty, setSelectedFaculty] = useState('');
    const [selectedSchool, setSelectedSchool] = useState('');
    const [selectedPlan, setSelectedPlan] = useState('');

    const [isLoading, setIsLoading] = useState(false);
    const [isPageLoading, setIsPageLoading] = useState(true);
    const [hasPendingRequest, setHasPendingRequest] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { setUser } = useAuthStore();

    const fetchInitialData = async () => {
        try {
            const reqsRes = await api.get('/accounts/student/membership-requests/');
            const requests: MembershipRequestData[] = reqsRes.data;
            const isPending = requests.some((req) => req.status === 'pending');

            setHasPendingRequest(isPending);

            if (!isPending) {
                const [facultiesRes, schoolsRes] = await Promise.all([
                    api.get('/institution/catalog/faculties/'),
                    api.get('/institution/catalog/schools/'),
                ]);

                setAllFaculties(facultiesRes.data);
                setAllSchools(schoolsRes.data);
            }
        } catch {
            toast.error('Hubo un problema al conectar con el servidor.');
        }
    };

    useEffect(() => {
        let mounted = true;
        const init = async () => {
            await fetchInitialData();
            if (mounted) setIsPageLoading(false);
        };
        init();
        return () => {
            mounted = false;
        };
    }, []);

    const handleManualRefresh = async () => {
        setIsPageLoading(true);
        try {
            const userRes = await api.get('/accounts/users/me/');
            const updatedUser = userRes.data;
            const isApproved =
                updatedUser.school_memberships && updatedUser.school_memberships.length > 0;

            setUser(updatedUser);
            if (!isApproved) await fetchInitialData();
        } catch {
            toast.error('No pudimos actualizar tu estado.');
        } finally {
            setIsPageLoading(false);
        }
    };

    const handleAreaChange = (areaValue: string) => {
        setSelectedArea(areaValue);
        setSelectedFaculty('');
        setSelectedSchool('');
        setSelectedPlan('');
        setPlans([]);
    };

    const handleFacultyChange = (facultyId: string) => {
        setSelectedFaculty(facultyId);
        setSelectedSchool('');
        setSelectedPlan('');
        setPlans([]);
    };

    const handleSchoolChange = async (schoolId: string) => {
        setSelectedSchool(schoolId);
        setSelectedPlan('');

        if (!schoolId) {
            setPlans([]);
            return;
        }

        try {
            const res = await api.get(`/curricula/catalog/plans/?school=${schoolId}`);
            setPlans(res.data);
        } catch {
            toast.error('Error al cargar los planes de estudio.');
        }
    };

    const submitRequest = async () => {
        setError(null);
        if (!selectedSchool || !selectedPlan) {
            setError('Debes seleccionar una escuela y un plan de estudios.');
            return false;
        }

        try {
            setIsLoading(true);
            await api.post('/accounts/student/membership-requests/', {
                school_id: selectedSchool,
                curriculum_plan_id: selectedPlan,
            });

            toast.success('Solicitud enviada correctamente.');
            setHasPendingRequest(true);
            return true;
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail || 'Error al enviar la solicitud.');
            } else {
                setError('Ocurrió un error inesperado.');
            }
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const filteredFaculties = allFaculties.filter((f) => f.area === selectedArea);

    const filteredSchools = allSchools.filter((s) => s.faculty.public_id === selectedFaculty);

    return {
        areaOptions: ACADEMIC_AREAS,
        filteredFaculties,
        filteredSchools,
        plans,
        selectedArea,
        selectedFaculty,
        selectedSchool,
        selectedPlan,
        isLoading,
        isPageLoading,
        hasPendingRequest,
        error,
        handleAreaChange,
        handleFacultyChange,
        handleSchoolChange,
        setSelectedPlan,
        submitRequest,
        handleManualRefresh,
    };
}
