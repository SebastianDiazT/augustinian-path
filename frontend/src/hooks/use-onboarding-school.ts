import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';

export interface Area {
    public_id: string;
    name: string;
}

export interface Faculty {
    public_id: string;
    area: string;
    name: string;
}

export interface ProfessionalSchool {
    public_id: string;
    faculty: string;
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

export function useOnboardingSchool() {
    const [allAreas, setAllAreas] = useState<Area[]>([]);
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
            const reqsRes = await api.get('/accounts/membership-requests/');
            const requests: MembershipRequestData[] = reqsRes.data.data || reqsRes.data;
            const isPending = requests.some((req) => req.status === 'pending');
            setHasPendingRequest(isPending);

            if (!isPending) {
                const [areasRes, facultiesRes, schoolsRes] = await Promise.all([
                    api.get('/institution/areas/'),
                    api.get('/institution/faculties/'),
                    api.get('/institution/professional-schools/'),
                ]);

                setAllAreas(areasRes.data.data || areasRes.data);
                setAllFaculties(facultiesRes.data.data || facultiesRes.data);
                setAllSchools(schoolsRes.data.data || schoolsRes.data);
            }
        } catch (err) {
            console.error('Error cargando datos:', err);
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
            const updatedUser = userRes.data.data;

            const isApproved =
                updatedUser.school_memberships && updatedUser.school_memberships.length > 0;

            setUser(updatedUser);

            if (!isApproved) {
                await fetchInitialData();
            }
        } catch (error) {
            console.error('Error al refrescar el estado:', error);
            toast.error('No pudimos actualizar tu estado. Inténtalo de nuevo.');
        } finally {
            setTimeout(() => {
                setIsPageLoading(false);
            }, 100);
        }
    };

    const handleAreaChange = (areaId: string) => {
        setSelectedArea(areaId);
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
            const plansRes = await api.get(`/curricula/curriculum-plans/?school=${schoolId}`);
            setPlans(plansRes.data.data || plansRes.data);
        } catch (err) {
            console.error('Error cargando planes:', err);
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
            await api.post('/accounts/membership-requests/', {
                school: selectedSchool,
                curriculum_plan: selectedPlan,
                request_type: 'initial_request',
            });

            toast.success('Solicitud enviada correctamente.');
            setHasPendingRequest(true);
            return true;
        } catch (err: unknown) {
            console.error('Error al enviar solicitud:', err);
            if (axios.isAxiosError(err)) {
                if (err.response?.data?.school) {
                    setError(err.response.data.school[0]);
                } else {
                    setError('Ocurrió un error al enviar tu solicitud. Inténtalo de nuevo.');
                }
            } else {
                setError('Ocurrió un error inesperado.');
            }
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    const filteredFaculties = allFaculties.filter((f) => f.area === selectedArea);
    const filteredSchools = allSchools.filter((s) => s.faculty === selectedFaculty);

    return {
        allAreas,
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
