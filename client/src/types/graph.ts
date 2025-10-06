import { type SearchItem } from "@/types/search"

export type TimeSeries = { x: number; y: number }

export type TimeSeriesWrapper = { abs: TimeSeries[]; rel: TimeSeries[] }

export type GraphItem = { searchItem: SearchItem; data: TimeSeriesWrapper; uuid: string }
