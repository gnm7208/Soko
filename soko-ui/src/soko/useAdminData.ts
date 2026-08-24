import { useEffect, useState } from "react";

import { api, type ApiAdminUser, type ApiDispute, type ApiListing, type ApiMetrics, type ApiPayoutRequest, type ApiShop } from "@/services/api";

interface AdminData {
  metrics: ApiMetrics | null;
  shops: ApiShop[];
  users: ApiAdminUser[];
  listings: ApiListing[];
  payouts: ApiPayoutRequest[];
  disputes: ApiDispute[];
  loading: boolean;
  refresh: () => void;
}

const emptyData: Omit<AdminData, "refresh"> = {
  metrics: null,
  shops: [],
  users: [],
  listings: [],
  payouts: [],
  disputes: [],
  loading: false,
};

export function useAdminData(isAdmin = false): AdminData {
  const [refreshToken, setRefreshToken] = useState(0);
  const [data, setData] = useState<Omit<AdminData, "refresh">>({ ...emptyData, loading: isAdmin });

  useEffect(() => {
    if (!isAdmin) {
      setData({ ...emptyData, loading: false });
      return;
    }
    let active = true;
    Promise.allSettled([
      api.getAdminMetrics(),
      api.getAdminShops({ status: "pending", page: 1, per_page: 100 }),
      api.getAdminUsers({ page: 1, per_page: 100 }),
      api.getAdminListings({ page: 1, per_page: 100 }),
      api.getAdminPayouts({ status: "pending", page: 1, per_page: 100 }),
      api.getAdminDisputes({ status: "open", page: 1, per_page: 100 }),
    ]).then(([metricsResult, shopsResult, usersResult, listingsResult, payoutsResult, disputesResult]) => {
      if (!active) return;
      setData({
        metrics: metricsResult.status === "fulfilled" ? metricsResult.value : null,
        shops: shopsResult.status === "fulfilled" ? shopsResult.value.items : [],
        users: usersResult.status === "fulfilled" ? usersResult.value.items : [],
        listings: listingsResult.status === "fulfilled" ? listingsResult.value.items : [],
        payouts: payoutsResult.status === "fulfilled" ? payoutsResult.value.items : [],
        disputes: disputesResult.status === "fulfilled" ? disputesResult.value.items : [],
        loading: false,
      });
    });
    return () => { active = false; };
  }, [isAdmin, refreshToken]);

  return { ...data, refresh: () => setRefreshToken((value) => value + 1) };
}
