import React, { Component } from "react";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import CustomPropTypes from "@/customPropTypes";
import * as Permission from "@/constants/permissions";
import AuthorizationWrapper from "@/components/common/wrappers/AuthorizationWrapper";
import {
  fetchMineReports,
  updateMineReport,
  createMineReport,
} from "@/actionCreators/reportActionCreator";
import AddButton from "@/components/common/AddButton";
import MineReportTable from "@/components/mine/Reports/MineReportTable";
import * as ModalContent from "@/constants/modalContent";
import { modalConfig } from "@/components/modalContent/config";
import { getMineReports } from "@/selectors/reportSelectors";

/**
 * @class  MinePermitInfo - contains all permit information
 */

const propTypes = {
  mine: CustomPropTypes.mine.isRequired,
  mineReports: PropTypes.arrayOf(PropTypes.objectOf(PropTypes.any)).isRequired,
  // mineReports: PropTypes.arrayOf(CustomPropTypes.mineReport),
  fetchMineReports: PropTypes.func.isRequired,
  updateMineReport: PropTypes.func.isRequired,
  createMineReport: PropTypes.func.isRequired,
  openModal: PropTypes.func.isRequired,
  closeModal: PropTypes.func.isRequired,
};

export class MineReportInfo extends Component {
  componentWillMount = () => {
    this.props.fetchMineReports();
  };

  handleEditReport = (values) => {
    this.props
      .updateMineReport(this.props.mine.mine_guid, values.report_guid, values)
      .then(() => this.props.closeModal());
  };

  handleAddReport = (values) => {
    this.props
      .createMineReport(this.props.mine.mine_guid, values)
      .then(() => this.props.closeModal());
  };

  openAddReportModal = (event) => {
    event.preventDefault();
    this.props.openModal({
      props: {
        onSubmit: this.handleAddReport,
        title: `Add report for ${this.props.mine.mine_name}`,
        mineGuid: this.props.mine.mine_guid,
        dropdownMineReportDefinitions: this.props.mineReportDefinitions,
      },
      content: modalConfig.ADD_REPORT,
    });
  };

  openEditReportModal = (event, report) => {
    event.preventDefault();

    this.props.openModal({
      props: {
        initialValues: report,
        onSubmit: this.handleEditReport,
        title: `Edit report for ${this.props.mine.mine_name}`,
        dropdownMineReportDefinitions: this.props.mineReportDefinitions,
      },
      content: modalConfig.EDIT_REPORT,
    });
  };

  render() {
    return (
      <div>
        <AuthorizationWrapper
          permission={Permission.CREATE}
          isMajorMine={this.props.mine.major_mine_ind}
        >
          <AddButton
            onClick={(event) =>
              this.openAddReportModal(
                event,
                this.handleAddReport,
                `${ModalContent.ADD_REPORT} to ${this.props.mine.mine_name}`
              )
            }
          >
            Add a Report
          </AddButton>
        </AuthorizationWrapper>
        <MineReportTable
          openEditReportModal={this.openEditReportModal}
          mineReports={this.props.mineReports}
        />
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  mineReports: getMineReports(state),
});

const mapDispatchToProps = (dispatch) =>
  bindActionCreators(
    {
      fetchMineReports,
      updateMineReport,
      createMineReport,
    },
    dispatch
  );

MineReportInfo.propTypes = propTypes;

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MineReportInfo);
